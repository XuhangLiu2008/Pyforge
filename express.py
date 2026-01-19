from filament_operation.filament import Filament
from filament_operation.sample import sample as Sample

class image_obj:
    path: str
    new_arrangement: bool

    def __init__(self, path: str, new_arrangement: bool):
        self.path = path
        self.new_arrangement = new_arrangement

def one(filament_image_path: str, new_arrangement: bool):
    filament_sample_result = Sample(filament_image_path, new_order = new_arrangement)

    filament_cal = Filament("test", "test")
    filament_cal.calculateCoefficients(filament_sample_result, True)

    return filament_cal.refractive_index, filament_cal.extinction_coefficient

def main():
    # image_paths = [
    #     image_obj(path = "filament_sample/Rose01.jpeg", new_arrangement = False),
    #     image_obj(path = "filament_sample/Rose02.jpeg", new_arrangement = False),
    #     image_obj(path = "filament_sample/Rose03.jpeg", new_arrangement = False),
    # ]

    image_paths = [
        image_obj(path = "filament_sample/filament03.png", new_arrangement = True),
        image_obj(path = "filament_sample/Orange_jan152026.png", new_arrangement = True),
    ]

    # image_paths = [
    #     image_obj(path = "filament_sample/filament01.png", new_arrangement = False),
    # ]
    
    for img in image_paths:
        ri, ec = one(img.path, img.new_arrangement)
        print(f"Image: {img.path}")
        print(f"Refractive Index: {ri}")
        print(f"Extinction Coefficient: {ec}")
        print("===================================")

if __name__ == "__main__":
    main()