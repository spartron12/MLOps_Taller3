

DROP_PENGUINS_TABLE = """
DROP TABLE IF EXISTS penguins_raw;

"""

DROP_PENGUINS_CLEAN_TABLE = """
DROP TABLE IF EXISTS penguins_clean;            
 """


CREATE_PENGUINS_TABLE_RAW = """ CREATE TABLE penguins_raw (
            species VARCHAR(50) NULL,
            island VARCHAR(50) NULL,
            bill_length_mm DOUBLE NULL,
            bill_depth_mm DOUBLE NULL,
            flipper_length_mm DOUBLE NULL,
            body_mass_g DOUBLE NULL,
            sex VARCHAR(10) NULL,
            year INT NULL
        )
        """

CREATE_PENGUINS_TABLE_CLEAN = """ CREATE TABLE penguins_clean (
    species INT NULL,
    bill_length_mm DOUBLE NULL,
    bill_depth_mm DOUBLE NULL,
    flipper_length_mm DOUBLE NULL,
    body_mass_g DOUBLE NULL,
    year INT NULL,
    island_Biscoe INT NULL,
    island_Dream INT NULL,
    island_Torgersen INT NULL,
    sex_female INT NULL,
    sex_male INT NULL
        );      
        """