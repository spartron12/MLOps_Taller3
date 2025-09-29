

DROP_TABLE = """
DROP TABLE IF EXISTS forest_raw;

"""

DROP_CLEAN_TABLE = """
DROP TABLE IF EXISTS forest_clean;            
 """

CREATE_TABLE_RAW = """ CREATE TABLE forest_raw (
            Elevation INT NULL,
            Aspect INT NULL,
            Slope INT NULL,
            Horizontal_Distance_To_Hydrology INT NULL,
            Vertical_Distance_To_Hydrology INT NULL,
            Horizontal_Distance_To_Roadways INT NULL,
            Hillshade_9am INT NULL,
            Hillshade_Noon INT NULL,
            Hillshade_3pm INT NULL,
            Horizontal_Distance_To_Fire_Points INT NULL,
            Wilderness_Area VARCHAR(50) NULL,
            Soil_Type VARCHAR(50) NULL,
            Cover_Type INT NULL
        )
        """

CREATE__TABLE_CLEAN = """ CREATE TABLE forest_clean (
            Elevation INT NULL,
            Aspect INT NULL,
            Slope INT NULL,
            Horizontal_Distance_To_Hydrology INT NULL,
            Vertical_Distance_To_Hydrology INT NULL,
            Horizontal_Distance_To_Roadways INT NULL,
            Hillshade_9am INT NULL,
            Hillshade_Noon INT NULL,
            Hillshade_3pm INT NULL,
            Horizontal_Distance_To_Fire_Points INT NULL,
            Cover_Type INT NULL,
            Wilderness_Area_Cache INT NULL,
            Wilderness_Area_Commanche INT NULL,
            Wilderness_Area_Neota INT NULL,
            Wilderness_Area_Rawah INT NULL,
            Soil_Type_C2702 INT NULL,
            Soil_Type_C2703 INT NULL,
            Soil_Type_C2704 INT NULL,
            Soil_Type_C2705 INT NULL,
            Soil_Type_C2706 INT NULL,
            Soil_Type_C2717 INT NULL,
            Soil_Type_C3502 INT NULL,
            Soil_Type_C4201 INT NULL,
            Soil_Type_C4703 INT NULL,
            Soil_Type_C4704 INT NULL,
            Soil_Type_C4744 INT NULL,
            Soil_Type_C4758 INT NULL,
            Soil_Type_C5101 INT NULL,
            Soil_Type_C6101 INT NULL,
            Soil_Type_C6102 INT NULL,
            Soil_Type_C6731 INT NULL,
            Soil_Type_C7101 INT NULL,
            Soil_Type_C7102 INT NULL,
            Soil_Type_C7103 INT NULL,
            Soil_Type_C7201 INT NULL,
            Soil_Type_C7202 INT NULL,
            Soil_Type_C7700 INT NULL,
            Soil_Type_C7701 INT NULL,
            Soil_Type_C7702 INT NULL,
            Soil_Type_C7709 INT NULL,
            Soil_Type_C7710 INT NULL,
            Soil_Type_C7745 INT NULL,
            Soil_Type_C7746 INT NULL,
            Soil_Type_C7755 INT NULL,
            Soil_Type_C7756 INT NULL,
            Soil_Type_C7757 INT NULL,
            Soil_Type_C7790 INT NULL,
            Soil_Type_C8703 INT NULL,
            Soil_Type_C8707 INT NULL,
            Soil_Type_C8708 INT NULL,
            Soil_Type_C8771 INT NULL,
            Soil_Type_C8772 INT NULL,
            Soil_Type_C8776 INT NULL
        )
        """