
class StatusAssigner:
    @staticmethod
    def bad_status(message):
        return {'status':'error','error_reason':message }
    
    @staticmethod
    def good_status():
        return {'status':'accepted'}
    
    
    
    


