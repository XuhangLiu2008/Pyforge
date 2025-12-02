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
};

torch::Tensor SurfReflct(Filament a, Filament b) {
    return torch::pow((a.refractive_index - b.refractive_index) / (a.refractive_index + b.refractive_index), 2);
}

torch::Tensor LambertEffct(Filament a, float d) {
    return torch::exp( -1 * a.extinction_coefficient * d);
}



int main() {
    torch::Tensor x = torch::rand({2, 3});
    cout << "Random Tensor:\n" << x << endl;
    return 0;
}