import xml.etree.ElementTree as ET

class Template:
    def __init__(self, image, default_xml):
        self.tree = ET.parse(default_xml)
        self.root = self.tree.getroot()
        self.image = image


    def add_template_objects(self, xml, **kargs):
        tree = ET.parse(xml)
        root = tree.getroot()
        y_offset = kargs["y_offset"] if("y_offset" in kargs) else 0

        for _object in root.findall('./object'):
            print(_object.find('name').text)
            for bndbox in _object.findall('bndbox'):
                bndbox.find('ymin').text = str(int(bndbox.find('ymin').text)+y_offset)
                bndbox.find('ymax').text = str(int(bndbox.find('ymax').text)+y_offset)
            self.root.insert(7, _object)

        pass

    def random_crop_img(self):
        ## get random img from ext_images
        img = cv2.open(rand_img_path)

        pass

    def save(self, path):
        self.tree.write(path)

def create_battlefield(img, handcards, enemy_minions, player_minions, heropower_enemy, heropower_player):
    t = Template(img, "templates/battlefield/defaults.xml")
    t.add_template_objects("templates/battlefield/handcards_{}.xml".format(handcards))
    if(player_minions > 0):
        t.add_template_objects("templates/battlefield/minions_{}.xml".format(player_minions))
    if(enemy_minions > 0):
        t.add_template_objects("templates/battlefield/minions_{}.xml".format(enemy_minions), y_offset=-185)
    if(heropower_enemy):
        t.add_template_objects("templates/battlefield/heropower_enemy.xml")
    if(heropower_player):
        t.add_template_objects("templates/battlefield/heropower_player.xml")
    t.save("test.xml")
