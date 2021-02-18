import json
class NotificationMessages:

    @staticmethod
    def order_creation(order):
        """
            It notify only to all the connected staff of a store
            """
        message_string= f"Nueva Orden"
        message_data = {"client_name":order.buyer.first_name, "order_slug": order.slug, "identifier_id" : str(order.store.id), "order_status": order.str_order_status, "message": message_string}
        message_object = {"data" : message_data}

        return json.dumps(message_object)


    @staticmethod
    def order_cancel_by_client(order):
        message_string= f"Tu Orden ha sido cancelada"
        message_data = {"client_name":order.buyer.first_name,"order_slug": order.slug, "identifier_id" : str(order.store.id), "order_status": order.str_order_status, "message": message_string}
        message_object = {"data" : message_data}

        return json.dumps(message_object)

    @staticmethod
    def order_cancel_by_store(order):
        message_string= f"Tu Orden no ha sido aceptada"
        message_data = {"client_name":order.buyer.first_name,"order_slug": order.slug, "identifier_id" : order.buyer.email, "order_status": order.str_order_status, "message": message_string}
        message_object = {"data" : message_data}

        return json.dumps(message_object)
    
    @staticmethod
    def order_aceptada(order):
        message_string= f"Tu Orden ha sido aceptada por {order.store.store.name}"
        message_data = {"client_name":order.buyer.first_name,"order_slug": order.slug, "identifier_id" : order.buyer.email, "order_status": order.str_order_status, "message": message_string}
        message_object = {"data" : message_data}

        return json.dumps(message_object)

    @staticmethod
    def order_to_deliver(order):
        message_string= f"Estamos buscando delivery para tu orden"
        message_data = {"identifier_id" : order.buyer.email, "order_slug": order.slug, "order_status": order.str_order_status, "message": message_string, "store_ubication":  order.store.location.geo}
        message_object = {"data" : message_data}

        return json.dumps(message_object)

    
    @staticmethod
    def order_on_delivery(order):
        message_string= f"Delivery asignado"
        message_data = {"client_name":order.buyer.first_name,"order_slug": order.slug, "identifier_id" : order.buyer.email, "order_status": order.str_order_status, "message": message_string}
        message_object = {"data" : message_data}

        return json.dumps(message_object)

    
    @staticmethod
    def order_completed(order):
        message_string= f"Orden entregada"
        message_data = {"client_name":order.buyer.first_name,"order_slug": order.slug, "identifier_id" : order.buyer.email, "order_status": order.str_order_status, "message": message_string}
        message_object = {"data" : message_data}

        return json.dumps(message_object)


