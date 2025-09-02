class StorageService:
    def save_material(self, material, archivo, mimetype):
        material.archivo = archivo
        material.mimetype = mimetype
        return material
    def get_material_file(self, material):
        return material.archivo, material.mimetype
