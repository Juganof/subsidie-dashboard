import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import os

def clean_euro_amount(amount_str):
    """Converteer een string met eurobedrag naar een float"""
    if not isinstance(amount_str, str):
        return np.nan
    # Verwijder euro teken en spaties, vervang komma's door punten
    clean_str = amount_str.replace('€', '').replace(' ', '').strip()
    try:
        # Converteer naar float
        return float(clean_str.replace(',', '.'))
    except ValueError:
        return np.nan

def extract_power_range(power_value):
    """Bepaal de vermogensklasse voor een specifiek vermogen"""
    if pd.isna(power_value):
        return "Onbekend"
    
    power = float(power_value)
    if power < 5:
        return "< 5 kW"
    elif power < 10:
        return "5-10 kW"
    elif power < 15:
        return "10-15 kW"
    elif power < 20:
        return "15-20 kW"
    else:
        return "> 20 kW"

def analyze_warmtepomp_data(file_path):
    """Analyseer data uit de meldcodelijst en bereken statistieken"""
    print(f"Analyzing data from: {file_path}")
    
    try:
        # Probeer eerst het bestand te lezen met ExcelFile om de sheets te identificeren
        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_name = "Meldcodes"
            if sheet_name not in excel_file.sheet_names:
                # Als de naam niet exact overeenkomt, zoek dan naar een vergelijkbare naam
                for name in excel_file.sheet_names:
                    if "meld" in name.lower():
                        sheet_name = name
                        break
                else:
                    # Als geen vergelijkbare naam is gevonden, gebruik de eerste sheet
                    sheet_name = excel_file.sheet_names[0]
            
            # Lees de geselecteerde sheet
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        except Exception as e:
            print(f"Error reading Excel file with ExcelFile: {e}")
            # Fallback: directe lezing proberen
            df = pd.read_excel(file_path)
        
        # Controleer of het dataframe leeg is of te weinig rijen heeft
        if df.empty or len(df) < 5:
            # Probeer met skiprows als we denken dat er headers zijn
            try:
                df = pd.read_excel(file_path, skiprows=10)
                print(f"Read with skiprows=10, shape: {df.shape}")
            except Exception as e:
                print(f"Error reading Excel with skiprows: {e}")
        
        # Controleer welke kolommen we hebben
        print("Kolommen in bestand:", df.columns.tolist())
        
        # Maak kopie om veilig te bewerken
        wp_data = df.copy()
        
        # Zoek de juiste subsidiekolom (verschillende bestanden kunnen verschillende namen hebben)
        subsidie_gevonden = False
        
        # 1. Zoek eerst op kolomnaam
        subsidie_kolommen = ["SUBSIDIE", "Subsidie", "subsidiebedrag", "SUBSIDIEBEDRAG", "Subsidiebedrag"]
        for kolom in subsidie_kolommen:
            if kolom in wp_data.columns:
                wp_data["SUBSIDIE_BEDRAG"] = wp_data[kolom].apply(clean_euro_amount)
                subsidie_gevonden = True
                break
        
        # 2. Als niet gevonden, zoek op inhoud (kolommen met euro-teken)
        if not subsidie_gevonden:
            for col in wp_data.columns:
                # Check een steekproef van waarden in de kolom
                sample_values = wp_data[col].dropna().astype(str).head(10).tolist()
                if any("€" in str(val) for val in sample_values):
                    wp_data["SUBSIDIE_BEDRAG"] = wp_data[col].apply(clean_euro_amount)
                    subsidie_gevonden = True
                    break
        
        # Zoek de juiste kolom voor vermogen
        vermogen_col = None
        vermogen_kolommen = ["VERMOGEN", "Vermogen", "KW", "kW", "VERMOGEN (KW)"]
        
        # 1. Zoek eerst op kolomnaam
        for kolom in vermogen_kolommen:
            if kolom in wp_data.columns:
                vermogen_col = kolom
                break
        
        # 2. Als niet gevonden, zoek op positie (vaak is vermogen de 4e kolom)
        if not vermogen_col and len(wp_data.columns) >= 4:
            # Check of de 4e kolom numeriek is
            if pd.api.types.is_numeric_dtype(wp_data.iloc[:, 3]):
                vermogen_col = wp_data.columns[3]
        
        # Voeg vermogensklasse toe
        if vermogen_col:
            try:
                wp_data["VERMOGENSKLASSE"] = wp_data[vermogen_col].apply(extract_power_range)
            except Exception as e:
                print(f"Error creating power class: {e}")
                # Fallback: maak een standaard vermogensklasse aan
                wp_data["VERMOGENSKLASSE"] = "Onbekend"
        else:
            print("Geen vermogenskolom gevonden, standaard vermogensklasse toegevoegd")
            wp_data["VERMOGENSKLASSE"] = "Onbekend"
        
        # Zoek de juiste categorie kolom
        categorie_col = None
        categorie_kolommen = ["CATEGORIE", "Categorie", "TYPE", "Type", "SOORT"]
        
        # 1. Zoek eerst op kolomnaam
        for kolom in categorie_kolommen:
            if kolom in wp_data.columns:
                categorie_col = kolom
                break
        
        # 2. Als niet gevonden, ga ervan uit dat de laatste kolom de categorie bevat
        if not categorie_col and len(wp_data.columns) > 5:
            categorie_col = wp_data.columns[-1]
            # Controleer of deze kolom tekstwaarden bevat
            if not pd.api.types.is_string_dtype(wp_data[categorie_col]):
                # Als het geen tekst is, probeer de kolom ervoor
                if len(wp_data.columns) > 6:
                    categorie_col = wp_data.columns[-2]
        
        # Als er nog steeds geen categoriekolom is gevonden, maak een standaard aan
        if not categorie_col:
            print("Geen categoriekolom gevonden, standaard categorie toegevoegd")
            wp_data["Categorie"] = "Onbekend"
            categorie_col = "Categorie"
        
        # Berekeningen uitvoeren
        resultaten = {}
        
        # 1. Gemiddelde subsidie per type warmtepomp
        if categorie_col and "SUBSIDIE_BEDRAG" in wp_data.columns:
            # Verwijder rijen zonder subsidie
            valid_rows = wp_data.dropna(subset=["SUBSIDIE_BEDRAG"])
            
            if not valid_rows.empty:
                per_category = valid_rows.groupby(categorie_col)["SUBSIDIE_BEDRAG"].agg(
                    gemiddelde_subsidie=np.mean,
                    mediaan_subsidie=np.median,
                    min_subsidie=np.min,
                    max_subsidie=np.max,
                    aantal=len
                ).reset_index()
                
                resultaten["per_type"] = per_category
                print("\nGemiddelde subsidie per type warmtepomp:")
                print(per_category.to_string(index=False))
        
        # 2. Gemiddelde subsidie per vermogensklasse
        if "VERMOGENSKLASSE" in wp_data.columns and "SUBSIDIE_BEDRAG" in wp_data.columns:
            # Verwijder rijen zonder subsidie
            valid_rows = wp_data.dropna(subset=["SUBSIDIE_BEDRAG"])
            
            if not valid_rows.empty:
                per_vermogen = valid_rows.groupby("VERMOGENSKLASSE")["SUBSIDIE_BEDRAG"].agg(
                    gemiddelde_subsidie=np.mean,
                    mediaan_subsidie=np.median,
                    min_subsidie=np.min,
                    max_subsidie=np.max,
                    aantal=len
                ).reset_index()
                
                # Sorteer op vermogensklasse
                vermogensklasse_volgorde = ["< 5 kW", "5-10 kW", "10-15 kW", "15-20 kW", "> 20 kW", "Onbekend"]
                per_vermogen["VERMOGENSKLASSE"] = pd.Categorical(
                    per_vermogen["VERMOGENSKLASSE"], 
                    categories=vermogensklasse_volgorde, 
                    ordered=True
                )
                per_vermogen = per_vermogen.sort_values("VERMOGENSKLASSE")
                
                resultaten["per_vermogensklasse"] = per_vermogen
                print("\nGemiddelde subsidie per vermogensklasse:")
                print(per_vermogen.to_string(index=False))
        
        # 3. Combinatie van type en vermogensklasse
        if categorie_col and "VERMOGENSKLASSE" in wp_data.columns and "SUBSIDIE_BEDRAG" in wp_data.columns:
            # Verwijder rijen zonder subsidie
            valid_rows = wp_data.dropna(subset=["SUBSIDIE_BEDRAG"])
            
            if not valid_rows.empty:
                per_type_vermogen = valid_rows.groupby([categorie_col, "VERMOGENSKLASSE"])["SUBSIDIE_BEDRAG"].agg(
                    gemiddelde_subsidie=np.mean,
                    mediaan_subsidie=np.median,
                    min_subsidie=np.min,
                    max_subsidie=np.max,
                    aantal=len
                ).reset_index()
                
                resultaten["per_type_vermogen"] = per_type_vermogen
                print("\nGemiddelde subsidie per type en vermogensklasse:")
                print(per_type_vermogen.to_string(index=False))
        
        # 4. Bereken ratio subsidie vs. gemiddeld vermogen
        if vermogen_col and "SUBSIDIE_BEDRAG" in wp_data.columns:
            # Gebruik alleen rijen waar beide waarden aanwezig zijn
            valid_rows = wp_data[pd.notna(wp_data[vermogen_col]) & pd.notna(wp_data["SUBSIDIE_BEDRAG"])]
            if len(valid_rows) > 0:
                try:
                    valid_rows["SUBSIDIE_PER_KW"] = valid_rows["SUBSIDIE_BEDRAG"] / valid_rows[vermogen_col].astype(float)
                    
                    per_kw_stats = valid_rows.groupby(categorie_col)["SUBSIDIE_PER_KW"].agg(
                        gemiddelde_subsidie_per_kw=np.mean,
                        mediaan_subsidie_per_kw=np.median
                    ).reset_index()
                    
                    resultaten["subsidie_per_kw"] = per_kw_stats
                    print("\nGemiddelde subsidie per kW:")
                    print(per_kw_stats.to_string(index=False))
                except Exception as e:
                    print(f"Error calculating subsidy per kW: {e}")
        
        return resultaten, wp_data
        
    except Exception as e:
        print(f"Error analyzing file: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def integreer_met_app(statistieken, vermogen=None, type_wp=None):
    """
    Genereer relevante statistieken voor de app, gefilterd op vermogen en type
    
    Args:
        statistieken: Dict met statistieken uit analyze_warmtepomp_data
        vermogen: Float met het vermogen waarvoor statistieken moeten worden getoond
        type_wp: String met het type warmtepomp (bijv. "Lucht-Water")
    
    Returns:
        Dict met relevante statistieken
    """
    if statistieken is None:
        return {"error": "Geen statistieken beschikbaar"}
    
    resultaat = {}
    
    # Bepaal vermogensklasse als vermogen is opgegeven
    vermogensklasse = None
    if vermogen is not None:
        vermogensklasse = extract_power_range(vermogen)
        resultaat["gevraagd_vermogen"] = vermogen
        resultaat["vermogensklasse"] = vermogensklasse
    
    # Filter statistieken op basis van type en/of vermogensklasse
    if "per_type_vermogen" in statistieken and (type_wp or vermogensklasse):
        df = statistieken["per_type_vermogen"]
        
        if type_wp and vermogensklasse:
            # Filter op zowel type als vermogensklasse
            filtered = df[(df.iloc[:, 0].str.contains(type_wp, case=False)) & 
                          (df["VERMOGENSKLASSE"] == vermogensklasse)]
        elif type_wp:
            # Filter alleen op type
            filtered = df[df.iloc[:, 0].str.contains(type_wp, case=False)]
        elif vermogensklasse:
            # Filter alleen op vermogensklasse
            filtered = df[df["VERMOGENSKLASSE"] == vermogensklasse]
        
        if not filtered.empty:
            resultaat["gefilterde_statistieken"] = filtered.to_dict(orient="records")
    
    # Voeg algemene statistieken toe
    if "per_type" in statistieken:
        resultaat["statistieken_per_type"] = statistieken["per_type"].to_dict(orient="records")
    
    if "per_vermogensklasse" in statistieken:
        resultaat["statistieken_per_vermogensklasse"] = statistieken["per_vermogensklasse"].to_dict(orient="records")
    
    return resultaat

def generate_subsidie_overzicht(vermogen=None, type_wp=None):
    """
    Genereer een subsidie-overzicht voor gebruik in de app
    
    Args:
        vermogen: Opgegeven vermogen
        type_wp: Type warmtepomp
    
    Returns:
        Dict met subsidie-informatie
    """
    file_path = "Meldcodelijst Warmtepompen - april 2025 (3).xlsx"
    stats, data = analyze_warmtepomp_data(file_path)
    
    if stats is None:
        return {"error": "Kon geen statistieken genereren"}
    
    return integreer_met_app(stats, vermogen, type_wp)

if __name__ == "__main__":
    # Test de analyse
    file_path = "Meldcodelijst Warmtepompen - april 2025 (3).xlsx"
    stats, data = analyze_warmtepomp_data(file_path)
    
    # Voorbeeld: Genereer overzicht voor een lucht-water warmtepomp van 5 kW
    print("\n\nVOORBEELD SUBSIDIE-OVERZICHT:")
    overzicht = generate_subsidie_overzicht(5.0, "Lucht")
    
    # Toon het overzicht
    import json
    print(json.dumps(overzicht, indent=2)) 