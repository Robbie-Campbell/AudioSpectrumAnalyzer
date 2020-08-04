from PlayerAssets.Player import Player


def main():
    def items(current_inventory):
        full_inventory = ""
        punctuation = ", "
        player_stuff = current_inventory.inventory
        for index, item in enumerate(player_stuff):
            full_inventory += (item + punctuation)
            if index == len(player_stuff) - 2:
                punctuation = ""
                full_inventory += " and a "

        return full_inventory
    print("Hello and welcome to Rab's crazy adventure!")
    player_name = input("Please enter your characters name: ")
    game = Player(player_name.upper())
    intro = "{} You are a brave adventurer looking to save the kingdom!" \
            " You are equipped with {}, Good luck!".format(game.name, items(game))
    print(intro)


if __name__ == "__main__":
    main()
