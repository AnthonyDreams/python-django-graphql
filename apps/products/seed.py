from .models import Type


def TypeSeed():
    food_types = ['American', 'Pizza', 'Healthy', 'Vegetarian', 'Chinese', 'Hamburgers', 'Dessert', 'Chicken', 'Indian']
    type_icon = 1
    try:
        for food_type in food_types:
            type = Type(type_name=food_type, type_icon=str(type_icon)+ '.png')
            type.save()
            type_icon += 1

    except:
        return False
 
    return True