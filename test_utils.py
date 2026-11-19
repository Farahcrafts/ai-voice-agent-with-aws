import time
import datetime
import inspect

# 1. Le fameux interrupteur
DEBUG = True

# 2. Le journal
def debug_print(message):
    if DEBUG:
        functionName = inspect.stack()[1].function
        if functionName == "time_it" or functionName == "time_it_async":
            functionName = inspect.stack()[2].function
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {functionName} -> {message}")
        print(f"inspect.stack()[0].function: {inspect.stack()[0].function}")
        print(f"inspect.stack()[1].function: {inspect.stack()[1].function}")
        print(f"inspect.stack()[2].function: {inspect.stack()[2].function}")



# 3. Le chronomètre
def time_it(label, methodToRun):
    start_time = time.perf_counter()
    result = methodToRun()
    end_time = time.perf_counter()
    debug_print(f"Execution time for {label}: {end_time - start_time:.4f} seconds")
    return result

# --- TESTONS ! ---

def ma_tache_lente():
    time.sleep(0.5) # Simule un calcul qui prend 0.5 seconde
    return "Tâche terminée !"

#Ceci rend <module> comme functionName
print("--- Début du test ---")
resultat = time_it("Ma_Tache_Lente", ma_tache_lente)
print(f"Résultat récupéré : {resultat}")

#Ceci rend le nom de la fct "lancer_le_test" au lieu de module
def lancer_le_test():
    print("--- Début du test ---")
    resultat = time_it("Ma_Tache_Lente", ma_tache_lente)
    print(f"Résultat récupéré : {resultat}")

# On appelle la fonction
lancer_le_test()