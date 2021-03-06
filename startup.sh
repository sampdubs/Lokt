normal=$'\e[0m'
purple=$(tput setaf 5);
bold=$(tput bold)
purple="$bold$purple"
echo "${purple}This script will create the correct directory structure and install a couple dependencies for the Lokt Password manager.${normal}"
while true; do
    read -p "${purple}Do you wish to continue? (y/n) ${normal}" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) echo "${purple}Too bad, this script sure does make making the app a whole lot easier ;)${normal}" && exit;;
        * ) echo "${purple}Please answer yes or no.${normal}";;
    esac
done

rc_file="$HOME/.bashrc"
if [ $0 == "zsh" ]; then
    rc_file="$HOME/.zshrc"
fi

### Install software dependencies
command_name=brew
if ! type "$command_name" > /dev/null; then
    echo -e "\n${purple}Installing Homebrew${normal}\n"
    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
else
    echo -e "\n${purple}Homebrew already exists, updating homebrew.${normal}\n"
    brew update
fi

for command_name in node yarn watchman pyenv
do
    echo -e "\n\n${purple}Installing/upgrading $command_name.${normal}\n"
    brew install $command_name
    brew upgrade $command_name
done

brew link node
npm install -g npm

command_name=xcode-select
if ! type "$command_name" > /dev/null; then
    echo -e "\n${purple}Installing Xcode command line tools.${normal}\n"
    $command_name --install
else
    echo -e "\n${purple}Xcode command line tools already exists, skipping install.${normal}\n"
fi

echo -e "\n${purple}Installing React Native dependencies using homebrew and npm.${normal}\n"
brew tap AdoptOpenJDK/openjdk
brew cask install adoptopenjdk8
npm install -g react-native-cli@2.0.1

echo -e "\n\n${purple}Installing fbs/PyQt5 dependencies using pyenv and pip, this might take a while.${normal}\n\n"
pyenv init
echo -e "\n eval \"$(pyenv init -)\"" >> $rc_file
pyenv local 3.6.0
if [ "$(python -c 'import platform; print(platform.python_version())')" != "3.6.0" ]; then  
    PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.6.0
    pyenv local 3.6.0
fi
pip install --upgrade pip
echo -e "\n\n${purple}Setting up python virtual environment${normal}\n\n"
pip install virtualenv
virtualenv Lokt-venv
source Lokt-venv/bin/activate

pip install -Ur requirements.txt
pip install PyQt5==5.9.2

### Setting up FBS Project (Desktop client)
echo -e "\n\n${purple}Starting the fbs project. For app name, you should enter Lokt. You can just press enter through the next fields${normal}\n\n"
fbs startproject
rm -rf src/main/icons
mkdir target
mv lib/fbs/Icon.iconset target/Icon.iconset
mv lib/fbs/main.py src/main/python/main.py
mv lib/fbs/helpers.py src/main/python/helpers.py

### Setting up React Native Project (Mobile client)
echo -e "\n\n${purple}Starting the React Native project.${normal}\n\n"
react-native init --version="0.61.5" Lokt
cd Lokt
mv ../lib/react-native/helpers.js ../lib/react-native/App.js ../package-lock.json .
# npm install react-native@0.61.5 react-native-base64 crypto-js big-integer react-native-fs fernet buffer react-native-elements react-native-vector-icons
# npm i --save react-native-crypto
# npm i --save react-native-randombytes
# react-native link react-native-randombytes
# npm i --save-dev tradle/rn-nodeify
# ./node_modules/.bin/rn-nodeify --hack --install
# react-native link react-native-fs
npm ci
echo -e "\n\n${purple}Setting up cocoa pods.${normal}\n\n"
cd ios
pod repo update
mv ../../lib/react-native/Podflie Podfile
pod install
cd ..
npm install -g yo generator-rn-toolbox
yo rn-toolbox:assets --icon ../lib/react-native/icon.png
mv ../lib/react-native/fernet.js node_modules/fernet/fernet.js
mv ../lib/react-native/AppDelegate.h ios/Lokt/AppDelegate.h
cd ..

### Clean up
#rm -rf .git lib server startup.sh
echo -e "\n\n${purple}Everything is setup! You can now run 'fbs run' or 'cd Lokt && react-native run-(ios|android)'${normal}"
echo -e "${purple}To learn more about usage and building for the app, go to https://build-system.fman.io/ and https://facebook.github.io/react-native/${normal}\n\n"
