import json
import asyncio
import uuid

#Fake dynamo table avec l'operation qui sert a trouver l'utilisateur 
class FakeDynamoTable:
    """Une fausse table DynamoDB pour tester sans AWS"""
    def get_item(self, Key):
        # On simule une réponse d'AWS
        if Key['guestName'] == "John Doe":
            return {"Item": {"guestName": "John Doe", "dob": "1990-01-01", "loyaltyTier": "Gold"}}
        return {} # Retourne dict vide si le client n'existe pas

#Class ToolProcessor
class ToolProcessor:
    def __init__(self):
        self.tasks = {}
        self.guest_table = FakeDynamoTable() # On utilise notre fausse table

    #Creer un dictionnaire des tasks a executer avec _run_tool 
    #tool_name et tool_content c'est l'ia qui les demandent
    async def process_tool_async(self, tool_name, tool_content):
        task_id = str(uuid.uuid4())
        task = asyncio.create_task(self._run_tool(tool_name, tool_content))
        self.tasks[task_id] = task
        print(f"Task: {self.tasks[task_id]}")
        try:
            result = await task
            print(f"Resultat du task: {result}")
            return result
        finally:
            del self.tasks[task_id]

    #Fonction qui execute les tasks,
    # recherche le nom du tool et structure le content pour la fct prochaine
    async def _run_tool(self, tool_name, tool_content):
        tool = tool_name.lower()
        content = tool_content.get("content", {})
        print(f"tool: {tool}")
        print(f"content: {content}")

        if isinstance(content, str):
            content_data = json.loads(content)
        else:
            content_data = content

        if tool == "checkguestprofiletool":
            return self._execute_check_guest(content_data)
        return {"error": "Tool inconnu"}

    #Fonction qui fait la recherche dans la table et retourne les infos de l'utilisateur
    #content_data content structure qui vient de la fct _run_tool
    def _execute_check_guest(self, content_data):
        guest_name = content_data.get("guestName")

        #Nom du guest n'est pas obtenu
        if not guest_name:
            return {"error": "guestName is required."}

        #Recherche pas nom du guest obtenu
        response = self.guest_table.get_item(Key={'guestName': guest_name})

        #Nom du guest n'existe pas 
        if 'Item' not in response:
            return {"found": False, "message": "Guest not found."}

        #Si le nom du guest existe 
        item = response['Item']
        return {"found": True, "guestName": item['guestName'], "dob": item.get('dob')}

# --- TESTONS ! ---

async def main_test():
    processor = ToolProcessor()
    
    # Test 1 : Client existant
    print("Test 1: On cherche John Doe...")
    res1 = await processor.process_tool_async(
        "checkGuestProfileTool", 
        {"content": '{"guestName": "John Doe"}'} # On simule le JSON envoyé par l'IA
    )
    print("Résultat :", res1)

    # Test 2 : Client inconnu
    print("\nTest 2: On cherche Jane Doe...")
    res2 = await processor.process_tool_async(
        "checkGuestProfileTool", 
        {"content": '{"guestName": "Jane Doe"}'}
    )
    print("Résultat :", res2)

asyncio.run(main_test())