import graphene

class RateInput(graphene.InputObjectType):
    text = graphene.String()
    point = graphene.Float()