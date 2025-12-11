// USE a.out to run

#include <torch/torch.h>
#include <iostream>
#include <string>

using namespace std;

struct Filament {
    string brand;
    string name;
    torch::Tensor colour; // set by user, does not impact calculation
    torch::Tensor refractive_index;
    torch::Tensor extinction_coefficient;
    Filament(string brand, 
    string name, 
    torch::Tensor colour, 
    torch::Tensor refractive_index, 
    torch::Tensor extinction_coefficient); 
};

Filament::Filament(string brand, string name, 
    torch::Tensor colour, 
    torch::Tensor refractive_index, 
    torch::Tensor extinction_coefficient) {

    this->brand = brand;
    this->name = name;
    this->colour = colour;
    this->refractive_index = refractive_index;
    this->extinction_coefficient = extinction_coefficient;
}

torch::Tensor SurfReflct(Filament a, Filament b) {
    return torch::pow((a.refractive_index - b.refractive_index) / (a.refractive_index + b.refractive_index), 2);
}

torch::Tensor LambertEffct(Filament a, float d) {
    return torch::exp( -1 * a.extinction_coefficient * d);
}

class FilaMatch {

    static const int MAX_FILA = 105;
    static inline const Filament AIR = Filament("Nature", "Air", 
        torch::tensor({0, 0, 0}, torch::kUInt8),  // colour
        torch::tensor({1.0, 1.0, 1.0}),           // refractive index
        torch::tensor({0.0, 0.0, 0.0}));          // extinction coefficient
    
    public:
        int num_fila;
        Filament filaments[MAX_FILA];
        int max_layer;
        float32_t thickness;
    
    private:
        torch::Tensor P[MAX_FILA][MAX_FILA];
        torch::Tensor R[MAX_FILA][MAX_FILA];
}; 

int main() {
    torch::Tensor x = torch::rand({2, 3});
    cout << "Random Tensor:\n" << x << endl;
    return 0;
}