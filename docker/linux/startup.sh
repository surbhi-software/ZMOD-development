mkdir ~/.zmod
cp docker-compose.yml ~/.zmod/
cp ZMOD.sh ~/.zmod/
cp .env ~/.zmod/
sed -i "/alias ZMOD=/d" ~/.bashrc
sed -i "/alias zmod=/d" ~/.bashrc
echo alias ZMOD="~/.zmod/ZMOD.sh" >> ~/.bashrc
echo alias zmod="~/.zmod/ZMOD.sh" >> ~/.bashrc
chmod +x ~/.zmod/ZMOD.sh
source ~/.bashrc