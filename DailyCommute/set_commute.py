# Get the hour field from the referenced item
hour = int(_("Everyday 7:30&18:15").first().json.get("Hour", 0))

# Choose commute direction
if hour >= 13:
    time = "Evening"
    commute = [
        {
            "mode": "metro",
            "line": "M1",
            "direction": "Château de Vincennes",
            "from_stop": "Pont de Neuilly",
            "to_stop": "Charles de Gaulle - Étoile",
            "intermediate_stops": ["Les Sablons", "Porte Maillot", "Argentine"],
        },
        {
            "mode": "rer",
            "line": "RER A",
            "direction": "Eastbound",
            "from_stop": "Charles de Gaulle - Étoile",
            "to_stop": "Châtelet - Les Halles",
            "intermediate_stops": ["Auber"],
        },
        {
            "mode": "rer",
            "line": "RER B",
            "direction": "Southbound",
            "from_stop": "Châtelet - Les Halles",
            "to_stop": "La Croix de Berny",
            "intermediate_stops": [
                "Saint-Michel - Notre-Dame",
                "Luxembourg",
                "Port-Royal",
                "Denfert-Rochereau",
                "Cité Universitaire",
                "Gentilly",
                "Laplace",
                "Arcueil - Cachan",
                "Bagneux",
                "Bourg-la-Reine",
                "Parc de Sceaux",
            ],
        },
        {
            "mode": "tram",
            "line": "T10",
            "direction": "Clamart - Jardin Parisien",
            "from_stop": "La Croix de Berny",
            "to_stop": "Les Peintres",
            "intermediate_stops": ["Lavallée", "Petit-Châtenay", "Théâtre la Piscine"],
        },
    ]

else:
    time = "Morning"
    commute = [
        {
            "mode": "tram",
            "line": "T10",
            "direction": "La Croix de Berny",
            "from_stop": "Les Peintres",
            "to_stop": "La Croix de Berny",
            "intermediate_stops": ["Théâtre la Piscine", "Petit-Châtenay", "Lavallée"],
        },
        {
            "mode": "rer",
            "line": "RER B",
            "direction": "Northbound",
            "from_stop": "La Croix de Berny",
            "to_stop": "Châtelet - Les Halles",
            "intermediate_stops": [
                "Parc de Sceaux",
                "Bourg-la-Reine",
                "Bagneux",
                "Arcueil - Cachan",
                "Laplace",
                "Gentilly",
                "Cité Universitaire",
                "Denfert-Rochereau",
                "Port-Royal",
                "Luxembourg",
                "Saint-Michel - Notre-Dame",
            ],
        },
        {
            "mode": "rer",
            "line": "RER A",
            "direction": "Westbound",
            "from_stop": "Châtelet - Les Halles",
            "to_stop": "Charles de Gaulle - Étoile",
            "intermediate_stops": ["Auber"],
        },
        {
            "mode": "metro",
            "line": "M1",
            "direction": "La Défense",
            "from_stop": "Charles de Gaulle - Étoile",
            "to_stop": "Pont de Neuilly",
            "intermediate_stops": ["Argentine", "Porte Maillot", "Les Sablons"],
        },
    ]

# Return as JSON
return [{"json": {"time": time, "commute": str(commute)}}]
