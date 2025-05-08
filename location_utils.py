def get_location_info(latitude, longitude):
    """
    Returns province and district information based on coordinates.
    This is a simplified version - you might want to use a more accurate GIS solution.
    """
    # Simplified coordinate ranges for provinces
    provinces = {
        "Gauteng": [(-26.8, -25.2, 27.0, 29.5)],  # (min_lat, max_lat, min_lon, max_lon)
        "Mpumalanga": [(-27.5, -24.5, 28.5, 32.0)],
        "Limpopo": [(-25.0, -22.0, 26.5, 32.0)],
        "North West": [(-28.0, -24.5, 22.5, 28.0)],
        "Free State": [(-30.5, -26.5, 24.5, 29.5)],
        "KwaZulu-Natal": [(-31.0, -26.5, 29.0, 33.0)],
        "Eastern Cape": [(-33.5, -30.0, 24.0, 30.0)],
        "Western Cape": [(-34.5, -31.0, 18.0, 24.0)],
        "Northern Cape": [(-32.0, -26.5, 16.5, 25.5)]
    }
    
    # Simplified district information - you would want to expand this
    districts = {
        "Gauteng": {
            "Johannesburg": [(-26.4, -26.0, 27.8, 28.2)],
            "Tshwane": [(-25.9, -25.5, 28.0, 28.4)],
            "Ekurhuleni": [(-26.3, -26.0, 28.2, 28.6)]
        },
        "Mpumalanga": {
            "Nkangala": [(-26.5, -25.5, 28.5, 30.0)],
            "Gert Sibande": [(-27.5, -26.0, 29.0, 31.0)],
            "Ehlanzeni": [(-25.8, -24.5, 30.0, 32.0)]
        }
        # Add more districts as needed
    }
    
    province = "Unknown"
    district = "Unknown"
    
    # Find province
    for prov, bounds_list in provinces.items():
        for bounds in bounds_list:
            min_lat, max_lat, min_lon, max_lon = bounds
            if (min_lat <= latitude <= max_lat and 
                min_lon <= longitude <= max_lon):
                province = prov
                break
    
    # Find district if province is known
    if province in districts:
        for dist, bounds_list in districts[province].items():
            for bounds in bounds_list:
                min_lat, max_lat, min_lon, max_lon = bounds
                if (min_lat <= latitude <= max_lat and 
                    min_lon <= longitude <= max_lon):
                    district = dist
                    break
    
    return {
        "province": province,
        "district": district
    } 