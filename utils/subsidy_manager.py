"""
Beheerder voor subsidiespecificaties.
Met dit programma kunnen nieuwe subsidies worden toegevoegd, bestaande worden gewijzigd,
en kunnen subsidies worden verwijderd uit het configuratiebestand.
"""

import json
import os
import importlib
import config

def display_subsidy_schemes():
    """Toont alle beschikbare subsidieregelingen."""
    print("\nBeschikbare subsidieregelingen:")
    for scheme_key, scheme_data in config.SUBSIDY_SCHEMES.items():
        print(f"- {scheme_key}: {scheme_data['name']}")

def display_subsidy_details(scheme_key):
    """Toont details van een specifieke subsidieregeling."""
    if scheme_key not in config.SUBSIDY_SCHEMES:
        print(f"Subsidieregeling '{scheme_key}' niet gevonden.")
        return
    
    scheme_data = config.SUBSIDY_SCHEMES[scheme_key]
    print(f"\nDetails van {scheme_data['name']} ({scheme_key}):")
    
    for condition_key, condition_data in scheme_data['conditions'].items():
        print(f"\n  {condition_key.capitalize()}:")
        
        if isinstance(condition_data, dict) and all(isinstance(v, dict) for v in condition_data.values()):
            # Voor geneste maatregelen (zoals verschillende typen glas)
            for measure_key, measure_data in condition_data.items():
                print(f"    - {measure_key}: {measure_data.get('description', measure_key)}")
                for spec_key, spec_value in measure_data.items():
                    if spec_key != 'description':
                        print(f"      {spec_key}: {spec_value}")
        else:
            # Voor eenvoudige maatregelen
            for spec_key, spec_value in condition_data.items():
                print(f"    {spec_key}: {spec_value}")

def add_or_update_subsidy():
    """Voegt een nieuwe subsidieregeling toe of werkt een bestaande regeling bij."""
    display_subsidy_schemes()
    
    scheme_key = input("\nVoer de code in van de subsidieregeling (bijv. 'ISDE', 'EIA'): ").strip().upper()
    
    if scheme_key in config.SUBSIDY_SCHEMES:
        print(f"Subsidieregeling '{scheme_key}' bestaat al. Deze wordt bijgewerkt.")
        scheme_data = config.SUBSIDY_SCHEMES[scheme_key]
    else:
        print(f"Nieuwe subsidieregeling '{scheme_key}' wordt aangemaakt.")
        scheme_data = {'name': '', 'conditions': {}}
    
    scheme_data['name'] = input(f"Voer de naam in van de subsidieregeling [{scheme_data.get('name', '')}]: ").strip() or scheme_data.get('name', '')
    
    # Maatregelen bewerken
    edit_conditions(scheme_data)
    
    # Bijwerken in configuratie
    config.SUBSIDY_SCHEMES[scheme_key] = scheme_data
    save_config()
    print(f"Subsidieregeling '{scheme_key}' is bijgewerkt.")

def edit_conditions(scheme_data):
    """Bewerkt de voorwaarden van een subsidieregeling."""
    while True:
        print("\nBeschikbare maatregelen:")
        for i, condition in enumerate(scheme_data['conditions'].keys(), 1):
            print(f"{i}. {condition}")
        print(f"{len(scheme_data['conditions']) + 1}. Nieuwe maatregel toevoegen")
        print("0. Terug naar hoofdmenu")
        
        choice = input("\nKies een maatregel om te bewerken (nummer): ").strip()
        
        if choice == '0':
            break
        
        try:
            choice_num = int(choice)
            if choice_num == len(scheme_data['conditions']) + 1:
                # Nieuwe maatregel toevoegen
                new_condition = input("Voer de naam van de nieuwe maatregel in: ").strip().lower()
                if new_condition:
                    scheme_data['conditions'][new_condition] = {}
                    edit_measure(scheme_data['conditions'][new_condition])
            elif 1 <= choice_num <= len(scheme_data['conditions']):
                # Bestaande maatregel bewerken
                condition_key = list(scheme_data['conditions'].keys())[choice_num - 1]
                edit_measure(scheme_data['conditions'][condition_key])
            else:
                print("Ongeldige keuze.")
        except ValueError:
            print("Voer een geldig nummer in.")

def edit_measure(measure_data):
    """Bewerkt de specificaties van een maatregel."""
    is_nested = False
    
    # Controleer of dit een geneste maatregel is (zoals verschillende typen glas)
    if not measure_data:
        nested = input("Heeft deze maatregel verschillende typen/varianten? (j/n): ").strip().lower()
        is_nested = nested == 'j'
    else:
        # Als er al data is, bepaal of het genest is
        is_nested = any(isinstance(v, dict) for v in measure_data.values())
    
    if is_nested:
        edit_nested_measure(measure_data)
    else:
        edit_simple_measure(measure_data)

def edit_nested_measure(measure_data):
    """Bewerkt een geneste maatregel (zoals verschillende typen glas)."""
    while True:
        print("\nBeschikbare typen:")
        for i, measure_type in enumerate(measure_data.keys(), 1):
            description = measure_data[measure_type].get('description', measure_type)
            print(f"{i}. {measure_type} ({description})")
        print(f"{len(measure_data) + 1}. Nieuw type toevoegen")
        print("0. Terug")
        
        choice = input("\nKies een type om te bewerken (nummer): ").strip()
        
        if choice == '0':
            break
        
        try:
            choice_num = int(choice)
            if choice_num == len(measure_data) + 1:
                # Nieuw type toevoegen
                new_type = input("Voer de code van het nieuwe type in: ").strip().lower()
                if new_type:
                    description = input(f"Voer een beschrijving in voor {new_type}: ").strip()
                    measure_data[new_type] = {'description': description}
                    edit_simple_measure(measure_data[new_type])
            elif 1 <= choice_num <= len(measure_data):
                # Bestaand type bewerken
                measure_type = list(measure_data.keys())[choice_num - 1]
                edit_simple_measure(measure_data[measure_type])
            else:
                print("Ongeldige keuze.")
        except ValueError:
            print("Voer een geldig nummer in.")

def edit_simple_measure(specs):
    """Bewerkt de specificaties van een eenvoudige maatregel."""
    while True:
        print("\nHuidige specificaties:")
        for key, value in specs.items():
            print(f"- {key}: {value}")
        
        print("\nBewerkopties:")
        print("1. Eigenschap toevoegen/bewerken")
        print("2. Eigenschap verwijderen")
        print("0. Terug")
        
        choice = input("\nKies een optie: ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            key = input("Voer de naam van de eigenschap in: ").strip()
            if key in specs:
                current = specs[key]
                print(f"Huidige waarde: {current}")
                
                if isinstance(current, (int, float)):
                    try:
                        value = input(f"Voer een nieuwe waarde in [{current}] (leeg laten voor ongewijzigd): ").strip()
                        specs[key] = float(value) if value else current
                        # Converteer naar integer als het een geheel getal is
                        if specs[key] == int(specs[key]):
                            specs[key] = int(specs[key])
                    except ValueError:
                        print("Ongeldige numerieke waarde.")
                elif isinstance(current, bool):
                    value = input(f"Voer een nieuwe waarde in (true/false) [{current}]: ").strip().lower()
                    if value in ('true', 't', 'yes', 'y', '1'):
                        specs[key] = True
                    elif value in ('false', 'f', 'no', 'n', '0'):
                        specs[key] = False
                else:
                    value = input(f"Voer een nieuwe waarde in [{current}]: ").strip()
                    specs[key] = value or current
            else:
                # Nieuwe eigenschap
                value_type = input("Type van de waarde (tekst/getal/boolean): ").strip().lower()
                
                if value_type in ('getal', 'number', 'n'):
                    try:
                        value = float(input("Voer de numerieke waarde in: ").strip())
                        if value == int(value):
                            value = int(value)
                    except ValueError:
                        print("Ongeldige numerieke waarde. Standaardwaarde 0 wordt gebruikt.")
                        value = 0
                elif value_type in ('boolean', 'bool', 'b'):
                    bool_input = input("Voer true of false in: ").strip().lower()
                    value = bool_input in ('true', 't', 'yes', 'y', '1')
                else:
                    value = input("Voer de tekstwaarde in: ").strip()
                
                specs[key] = value
        elif choice == '2':
            key = input("Voer de naam in van de eigenschap die u wilt verwijderen: ").strip()
            if key in specs:
                confirm = input(f"Weet u zeker dat u '{key}' wilt verwijderen? (j/n): ").strip().lower()
                if confirm == 'j':
                    del specs[key]
                    print(f"Eigenschap '{key}' is verwijderd.")
            else:
                print(f"Eigenschap '{key}' niet gevonden.")
        else:
            print("Ongeldige keuze.")

def delete_subsidy():
    """Verwijdert een subsidieregeling."""
    display_subsidy_schemes()
    
    scheme_key = input("\nVoer de code in van de subsidieregeling die u wilt verwijderen: ").strip().upper()
    
    if scheme_key not in config.SUBSIDY_SCHEMES:
        print(f"Subsidieregeling '{scheme_key}' niet gevonden.")
        return
    
    confirm = input(f"Weet u zeker dat u '{scheme_key}: {config.SUBSIDY_SCHEMES[scheme_key]['name']}' wilt verwijderen? (j/n): ").strip().lower()
    
    if confirm == 'j':
        del config.SUBSIDY_SCHEMES[scheme_key]
        save_config()
        print(f"Subsidieregeling '{scheme_key}' is verwijderd.")
    else:
        print("Verwijderen geannuleerd.")

def save_config():
    """Slaat de huidige configuratie op in config.py."""
    config_content = f"""\"\"\"
Configuratiebestand voor subsidiespecificaties.
Alle specificaties van elke maatregel per subsidie worden hier gedefinieerd.
\"\"\"

# Database van subsidie regelingen (actuele gegevens 2025)
SUBSIDY_SCHEMES = {json.dumps(config.SUBSIDY_SCHEMES, indent=4, ensure_ascii=False)}"""
    
    # Vervang dubbele quotes door enkele quotes voor sleutels en strings
    # Dit zorgt voor betere leesbaarheid in Python-stijl
    import re
    config_content = re.sub(r'"(\w+)":', r'\1:', config_content)
    config_content = re.sub(r'": "', r'": \'', config_content)
    config_content = re.sub(r'",', r'\',', config_content)
    config_content = re.sub(r'"$', r'\'', config_content, flags=re.MULTILINE)
    
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)

def load_from_json():
    """Laadt subsidies vanuit een JSON-bestand."""
    file_path = input("Voer het pad naar het JSON-bestand in: ").strip()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            new_schemes = json.load(f)
        
        for key, data in new_schemes.items():
            config.SUBSIDY_SCHEMES[key] = data
        
        save_config()
        print(f"Subsidies uit '{file_path}' zijn succesvol geladen.")
    except FileNotFoundError:
        print(f"Bestand '{file_path}' niet gevonden.")
    except json.JSONDecodeError:
        print(f"Bestand '{file_path}' bevat geen geldige JSON.")
    except Exception as e:
        print(f"Fout bij laden van bestand: {e}")

def save_to_json():
    """Slaat subsidies op in een JSON-bestand."""
    file_path = input("Voer het pad in voor het JSON-bestand: ").strip()
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config.SUBSIDY_SCHEMES, f, indent=4, ensure_ascii=False)
        print(f"Subsidies zijn opgeslagen in '{file_path}'.")
    except Exception as e:
        print(f"Fout bij opslaan naar bestand: {e}")

def main():
    """Hoofdprogramma."""
    while True:
        print("\n===== SUBSIDIE BEHEERDER =====")
        print("1. Toon alle subsidieregelingen")
        print("2. Toon details van een subsidieregeling")
        print("3. Voeg subsidieregeling toe of werk bij")
        print("4. Verwijder subsidieregeling")
        print("5. Importeer vanuit JSON")
        print("6. Exporteer naar JSON")
        print("0. Afsluiten")
        
        choice = input("\nKies een optie: ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            display_subsidy_schemes()
        elif choice == '2':
            display_subsidy_schemes()
            scheme_key = input("\nVoer de code in van de subsidieregeling die u wilt bekijken: ").strip().upper()
            display_subsidy_details(scheme_key)
        elif choice == '3':
            add_or_update_subsidy()
        elif choice == '4':
            delete_subsidy()
        elif choice == '5':
            load_from_json()
        elif choice == '6':
            save_to_json()
        else:
            print("Ongeldige keuze. Probeer opnieuw.")

if __name__ == "__main__":
    main() 