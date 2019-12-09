mkdir ~/.zmod
cp docker-compose.yml ~/.zmod/
cp ZMODMacOS.sh ~/.zmod/
cp .env ~/.zmod/
sed -i '' -e "/alias ZMOD=/d" ~/.bashrc 
sed -i '' -e "/alias zmod=/d" ~/.bashrc
echo alias ZMOD="~/.zmod/ZMODMacOS.sh" >> ~/.bashrc
echo alias zmod="~/.zmod/ZMODMacOS.sh" >> ~/.bashrc
chmod +x ~/.zmod/ZMODMacOS.sh
source ~/.bashrc
