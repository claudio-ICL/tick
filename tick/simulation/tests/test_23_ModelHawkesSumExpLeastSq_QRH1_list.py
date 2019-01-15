# License: BSD 3 clause

import numpy as np
from tick.simulation import HawkesKernel0, HawkesKernelExp, HawkesKernelPowerLaw, \
    HawkesKernelSumExp
from tick.simulation import SimuHawkes

timestamps_list = []
global_n_list = []

n_nodes = 2
dim = n_nodes
MaxN_of_f = 10
f_i = [np.array([1., 0.7, 0.8, 0.6, 0.5, 0.8, 0.3, 0.6, 0.2, 0.7]), np.array([1., 0.6, 0.8, 0.8, 0.6, 0.6, 0.5, 0.8, 0.3, 0.6])]

end_time = 2000.0
end_times = []

betas = np.array([0.1, 2, 5])
U = len(betas)
kernels = np.array([
            [HawkesKernelSumExp(np.array([0.2, 0.15, 0.1]), betas), HawkesKernelSumExp(np.array([0.3, 0.1, 0.1]), betas)],
            [HawkesKernelSumExp(np.array([0., 0.2, 0.0]), betas), HawkesKernelSumExp(np.array([0., 0.4, 0.1]), betas)]
        ])

for num_simu in range(1000):
    seed = num_simu * 10086 + 3007
    simu_model = SimuHawkes(kernels=kernels, end_time=end_time, custom=True, seed=seed, MaxN_of_f=MaxN_of_f, f_i=f_i)
    for i in range(n_nodes):
        simu_model.set_baseline(i, 0.4 + 0.1 * i)
        for j in range(n_nodes):
            simu_model.set_kernel(i, j, kernels[i, j])
    simu_model.track_intensity(0.1)
    simu_model.simulate()

    timestamps = simu_model.timestamps
    timestamps.append(np.array([]))
    timestamps_list.append(timestamps)

    global_n = np.array(simu_model._pp.get_global_n())
    global_n = np.insert(global_n, 0, 0).astype(int)
    global_n_list.append(global_n)

    end_times.append(end_time)

end_times = np.array(end_times)
##################################################################################################################
from tick.optim.model.hawkes_fixed_sumexpkern_QRH1_leastsq_list import ModelHawkesFixedSumExpKernLeastSqQRH1List

model_list = ModelHawkesFixedSumExpKernLeastSqQRH1List(betas, MaxN_of_f, n_threads=8)
model_list.fit(timestamps_list, global_n_list, end_times=end_times)

x_real = np.array(
    [0.4, 0.5,   0.2, 0.15, 0.1,     0.3, 0.1, 0.1,     0., 0.2, 0.0,     0., 0.4, 0.1,
     1., 0.7, 0.8, 0.6, 0.5, 0.8, 0.3, 0.6, 0.2, 0.7,
     1., 0.6, 0.8, 0.8, 0.6, 0.6, 0.5, 0.8, 0.3, 0.6])
print(model_list.loss(x_real))


###################################################################
from tick.optim.solver import AGD
from tick.optim.prox import ProxZero, ProxL1

print('#' * 40)
print('tick.agd')
prox = ProxZero()
solver = AGD(step=1e-3, linesearch=False, max_iter=10000, print_every=50)
solver.set_model(model_list).set_prox(prox)
x0 = np.random.rand(model_list.n_coeffs)
solver.solve(x0)

coeff = solver.solution
for k in range(dim):
    fi0 = coeff[dim + U * dim * dim + k * MaxN_of_f]
    coeff[k] *= fi0
    coeff[dim + U * dim * k: dim + U * dim * (k + 1)] *= fi0
    coeff[dim + U * dim * dim + k * MaxN_of_f: dim + U * dim * dim + (k + 1) * MaxN_of_f] /= fi0
print(coeff)
print(model_list.loss(solver.solution))