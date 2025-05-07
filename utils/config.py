"""
Configuratiebestand voor subsidiespecificaties.
Alle specificaties van elke maatregel per subsidie worden hier gedefinieerd voor rijksmonumenten.
"""

# Database van subsidie regelingen (actuele gegevens 2025)
SUBSIDY_SCHEMES = {
    'ISDE': {
        'name': 'Investeringssubsidie Duurzame Energie',
        'conditions': {
            'glas': {
                'monument_hr_glas': {
                    'description': 'HR++ glas voor monumenten',
                    'min_u_value': 0.7,
                    'max_u_value': 2.0,
                    'subsidy_per_m2': 46,  # Per 2025
                    'double_subsidy_per_m2': 92,  # Bij 2 maatregelen
                    'min_area': 3,  # Minimaal te isoleren oppervlak vanaf 2025
                    'max_area': 45  # Maximaal aantal m² waarvoor subsidie
                },
                'monument_triple_glas': {
                    'description': 'HR+++ glas (triple glas) voor monumenten',
                    'max_u_value': 0.7,
                    'subsidy_per_m2': 65.5,  # Bedrag per vierkante meter vanaf 2025
                    'double_subsidy_per_m2': 131,  # Bij 2 maatregelen
                    'min_area': 3,  # Minimaal te isoleren oppervlak vanaf 2025
                    'max_area': 45  # Maximaal aantal m² waarvoor subsidie
                },
                'vacuum_glas': {
                    'description': 'Vacuümglas voor monumenten',
                    'min_u_value': 0.4,
                    'max_u_value': 0.7,
                    'subsidy_per_m2': 25,  # Zonder kozijnvervanging
                    'subsidy_per_m2_with_frame': 111,  # Met kozijnvervanging
                    'double_subsidy_per_m2': 50,  # Bij 2 maatregelen
                    'double_subsidy_per_m2_with_frame': 222,  # Bij 2 maatregelen met kozijn
                    'min_area': 3,  # Minimaal te isoleren oppervlak
                    'max_area': 45  # Maximaal aantal m² waarvoor subsidie
                },
                'hr_plus_plus_glas': {
                    'description': 'HR++ glas (standaard)',
                    'max_u_value': 1.2,
                    'subsidy_per_m2': 25,  # Per 2025
                    'double_subsidy_per_m2': 50,  # Bij 2 maatregelen
                    'min_area': 3,  # Minimaal te isoleren oppervlak vanaf 2025
                    'max_area': 45,  # Maximaal aantal m² waarvoor subsidie
                    'requirements': 'U-waarde maximaal 1,2 W/m²K'
                },
                'triple_glas': {
                    'description': 'Triple glas (HR+++ glas)',
                    'max_u_value': 0.7,
                    'subsidy_per_m2': 111,  # Per 2025 (verhoogd van €65.50)
                    'double_subsidy_per_m2': 222,  # Bij 2 maatregelen
                    'min_area': 3,  # Minimaal te isoleren oppervlak vanaf 2025
                    'max_area': 45,  # Maximaal aantal m² waarvoor subsidie
                    'requirements': 'Vervanging kozijnen verplicht met Uf-waarde max 1,5 W/m²K'
                },
                'isolerende_panelen_standaard': {
                    'description': 'Isolerende panelen (standaard)',
                    'max_u_value': 1.2,
                    'min_u_value': 0.7,
                    'subsidy_per_m2': 10,  # Bedrag per m²
                    'double_subsidy_per_m2': 20,  # Bij 2 maatregelen
                    'min_area': 3,  # Minimaal te isoleren oppervlak vanaf 2025
                    'max_area': 45,  # Maximaal aantal m² waarvoor subsidie
                    'requirements': 'Alleen in combinatie met HR++ of triple glas'
                },
                'isolerende_panelen_hoog': {
                    'description': 'Isolerende panelen (hoge isolatiewaarde)',
                    'max_u_value': 0.7,
                    'subsidy_per_m2': 45,  # Bedrag per m²
                    'double_subsidy_per_m2': 90,  # Bij 2 maatregelen
                    'min_area': 3,  # Minimaal te isoleren oppervlak vanaf 2025
                    'max_area': 45,  # Maximaal aantal m² waarvoor subsidie
                    'requirements': 'Alleen in combinatie met HR++ of triple glas'
                },
                'isolerende_deuren_standaard': {
                    'description': 'Isolerende deuren (standaard)',
                    'max_u_value': 1.5,
                    'min_u_value': 1.0,
                    'subsidy_per_m2': 25,  # Per 2025
                    'double_subsidy_per_m2': 50,  # Bij 2 maatregelen
                    'min_area': 3,  # Minimaal te isoleren oppervlak vanaf 2025
                    'max_area': 45,  # Maximaal aantal m² waarvoor subsidie
                    'requirements': 'Alleen in combinatie met HR++ of triple glas'
                },
                'isolerende_deuren_hoog': {
                    'description': 'Isolerende deuren (hoge isolatiewaarde)',
                    'max_u_value': 1.0,
                    'subsidy_per_m2': 111,  # Per 2025
                    'double_subsidy_per_m2': 222,  # Bij 2 maatregelen
                    'min_area': 3,  # Minimaal te isoleren oppervlak vanaf 2025
                    'max_area': 45,  # Maximaal aantal m² waarvoor subsidie
                    'requirements': 'Alleen in combinatie met HR++ of triple glas'
                }
            },
            'warmtepomp': {
                'lucht_water': {
                    'description': 'Lucht-water warmtepomp',
                    'min_cop': 3.5,
                    'subsidy_per_kw': 1500,
                    'max_subsidy': 5000
                },
                'water_water': {
                    'description': 'Water-water warmtepomp',
                    'min_cop': 4.0,
                    'subsidy_per_kw': 2000,
                    'max_subsidy': 6000
                },
                'hybride': {
                    'description': 'Hybride warmtepomp',
                    'min_cop': 3.5,
                    'subsidy_flat': 2500,
                    'max_subsidy': 2500
                }
            },
            'isolatie': {
                'dak': {
                    'description': 'Dakisolatie voor monumenten',
                    'min_r_value': 3.5,
                    'subsidy_per_m2': 30,
                    'double_subsidy_per_m2': 60,
                    'min_area': 20,
                    'max_area': 200
                },
                'gevel': {
                    'description': 'Gevelisolatie voor monumenten',
                    'min_r_value': 3.5,
                    'subsidy_per_m2': 38,
                    'double_subsidy_per_m2': 76,
                    'min_area': 20,
                    'max_area': 170
                },
                'vloer': {
                    'description': 'Vloerisolatie voor monumenten',
                    'min_r_value': 3.5,
                    'subsidy_per_m2': 16,
                    'double_subsidy_per_m2': 32,
                    'min_area': 20,
                    'max_area': 130
                },
                'spouw': {
                    'description': 'Spouwmuurisolatie voor monumenten',
                    'min_r_value': 1.1,
                    'subsidy_per_m2': 8,
                    'double_subsidy_per_m2': 16,
                    'min_area': 20,
                    'max_area': 170
                }
            },
            'zonneboiler': {
                'description': 'Zonneboiler voor monumenten',
                'min_aperture': 2.5,
                'subsidy_per_aperture': 600,
                'max_aperture': 10
            }
        }
    },
    'EIA': {
        'name': 'Energie-investeringsaftrek',
        'description': 'Fiscale regeling voor energiebesparende investeringen voor bedrijven',
        'conditions': {
            'min_investment': 2500,  # Minimale investering voor EIA
            'max_investment': 151000000,  # Maximale investering per jaar
            'percentage': 0.40,  # 40% fiscale aftrek
            'net_benefit': 0.103,  # 10,3% netto voordeel
            'glas': {
                'description': 'Isolerende beglazing voor bedrijfsgebouwen',
                'code': '210402',
                'min_u_value': 0,
                'max_u_value': 0.7,  # Max U-waarde voor EIA
                'max_per_m2': 400,  # Maximum per m² dat voor EIA in aanmerking komt
                'requirements': 'Meervoudig glas met een vacuüm of gasgevulde spouw'
            },
            'warmtepomp': {
                'lucht_water': {
                    'description': 'Warmtepomp (luchtgerelateerd)',
                    'code': '211104',
                    'min_cop': 4.6,  # Voor vermogens ≤ 70kW
                    'min_cop_high': 4.0,  # Voor vermogens > 70kW
                    'max_per_kw': 1400,  # Maximum per kW dat voor EIA in aanmerking komt
                    'requirements': 'Seizoensgebonden energie-efficiëntie conform NEN-EN 14825:2022'
                },
                'water_water': {
                    'description': 'Warmtepomp (bodemgerelateerd)',
                    'code': '211103',
                    'min_cop_closed': 5.2,  # Voor gesloten bodembron
                    'min_cop_open': 6.2,  # Voor open bodembron
                    'min_cop_halogenfree': 4.0,  # Voor halogeenvrij koudemiddel
                    'max_per_kw': 400,  # Maximum per kW voor afgiftenet
                    'requirements': 'Seizoensgebonden energie-efficiëntie conform NEN-EN 14825:2022'
                },
                'boiler': {
                    'description': 'Warmtepompboiler',
                    'code': '211102',
                    'min_cop': 3.0,
                    'requirements': 'COP ≥ 3,0 gemeten conform NEN-EN 16147:2023'
                }
            },
            'isolatie': {
                'description': 'Isolatie voor bestaande constructies',
                'code': '210403',
                'min_r_value_increase': 2.0,  # Minimale toename R-waarde
                'min_r_value_total': 5.0,  # Minimale totale R-waarde na isolatie
                'max_per_m2_walls': 70,  # Maximum per m² voor wanden
                'max_per_m2_floor': 50,  # Maximum per m² voor vloer of dak
                'max_per_m2_roof_white': 60  # Maximum per m² voor dak met witte dakbedekking
            }
        }
    },
    'SEEH': {
        'name': 'Subsidie Energiebesparing Eigen Huis',
        'conditions': {
            'minimum_measures': 2,
            'isolatie': {
                'dak': {
                    'min_r_value': 3.5,
                    'subsidy_per_m2': 20,
                    'min_area': 20
                },
                'gevel': {
                    'min_r_value': 3.5,
                    'subsidy_per_m2': 25,
                    'min_area': 20
                },
                'vloer': {
                    'min_r_value': 3.5,
                    'subsidy_per_m2': 7,
                    'min_area': 20
                },
                'spouw': {
                    'min_r_value': 1.1,
                    'subsidy_per_m2': 5,
                    'min_area': 20
                }
            },
            'glas': {
                'hr_glas': {
                    'max_u_value': 1.2,
                    'subsidy_per_m2': 35,
                    'min_area': 10
                },
                'triple_glas': {
                    'max_u_value': 0.7,
                    'subsidy_per_m2': 100,
                    'min_area': 10
                }
            }
        }
    }
} 