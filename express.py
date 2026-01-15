from filament import Filament
from filament_sample.sample import sample as Sample

def one(filament_image_path: str):
    filament_sample_result = Sample(filament_image_path)

    filament_cal = Filament("test", "test")
    filament_cal.calculateCoefficients(filament_sample_result, True)

    return filament_cal.refractive_index, filament_cal.extinction_coefficient

def main():
    image_paths = [
        "filament_sample/Rose01.jpeg",
        "filament_sample/Rose02.jpeg",
        "filament_sample/Rose03.jpeg",
    ]
    
    for image_path in image_paths:
        ri, ec = one(image_path)
        print(f"Image: {image_path}")
        print(f"Refractive Index: {ri}")
        print(f"Extinction Coefficient: {ec}")
        print("===================================")


if __name__ == "__main__":
    main()