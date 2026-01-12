import numpy as np
import matplotlib.pyplot as plt

from color_code_stim import ColorCode, NoiseModel

def logical_fail_prob_from_sim(d: int, rounds: int, shots: int, p: float, superdense=True, circuit_type="tri"):
    """
    d: code distance (odd: 3,5,7,...)
    rounds: QEC cycles
    shots: Monte Carlo shots
    p: physical error strength (uniform circuit noise; 패키지 제공)
    """
    noise = NoiseModel.uniform_circuit_noise(p)  # 문서 quick start에 있는 방식 :contentReference[oaicite:1]{index=1}

    cc = ColorCode(
        d=d,
        rounds=rounds,
        circuit_type=circuit_type,
        noise_model=noise,
        superdense_circuit=superdense,  # superdense syndrome extraction 지원 :contentReference[oaicite:2]{index=2}
    )
    num_fails, info = cc.simulate(shots=shots, full_output=True)
    return num_fails / shots

def fit_epsilon_from_PL(rounds_list, PL_list):
    """
    PL(n) = 0.5*(1-(1-2e)^n) 를 최소제곱으로 fit.
    """
    rounds_arr = np.array(rounds_list, dtype=float)
    PL_arr = np.array(PL_list, dtype=float)

    # e 후보를 로그스케일로 촘촘히 훑어서 SSE 최소 찾기
    # (ε가 작아질수록 d=7에서 중요)
    grid = np.concatenate([
        np.logspace(-7, -2, 400),   # 1e-7 ~ 1e-2
        np.linspace(1e-2, 0.2, 200) # 1e-2 ~ 0.2
    ])
    best_e, best_sse = None, float("inf")
    for e in grid:
        pred = 0.5 * (1 - (1 - 2*e)**rounds_arr)
        sse = float(np.sum((pred - PL_arr)**2))
        if sse < best_sse:
            best_sse = sse
            best_e = float(e)
    return best_e, best_sse

def run_distance_scaling(
    distances=(3,5,7),
    rounds_list=(1,2,3,4,5,7,10,15,20),
    p=1e-3,
    base_shots=50_000,
    max_shots=2_000_000,
    target_min_errors=200,
    superdense=True
):
    """
    target_min_errors: 각 (d,n) 조합에서 failures가 최소 이 정도는 관측되게 shots 증가
    """
    results = {}
    t0 = time.time()

    for d in distances:
        print(f"\n=== d={d} ===")
        PLs = []
        used_shots = []

        for r in rounds_list:
            shots = base_shots
            while True:
                PL = logical_fail_prob_from_sim(d=d, rounds=r, shots=shots, p=p, superdense=superdense)
                fails = int(round(PL * shots))
                # 오류 이벤트가 너무 적으면 샷 늘림
                if fails >= target_min_errors or shots >= max_shots:
                    break
                shots = min(max_shots, shots * 2)

            PLs.append(PL)
            used_shots.append(shots)
            print(f"  rounds={r:>2} | shots={shots:>7} | PL={PL:.6g} | fails~{fails}")

        eps, sse = fit_epsilon_from_PL(rounds_list, PLs)
        results[d] = {
            "rounds": list(rounds_list),
            "PL": PLs,
            "shots": used_shots,
            "epsilon": eps,
            "fit_sse": sse,
        }
        print(f"  -> fitted epsilon_d ≈ {eps:.6g} (SSE={sse:.3g})")

    print(f"\nTotal elapsed: {time.time()-t0:.1f}s")
    return results

# 🔧 여기서 p 값을 바꿔가며 threshold 아래/근처를 관찰하면 스케일링이 달라짐
results = run_distance_scaling(
    distances=(3,5,7),
    rounds_list=(1,2,3,4,5,7,10,15,20),
    p=1e-3,               # 시작값. 필요하면 2e-3, 5e-3 등으로 스윕
    base_shots=50_000,
    max_shots=2_000_000,
    target_min_errors=200,
    superdense=True
)

# PL(n) 그래프
plt.figure()
for d, info in results.items():
    plt.plot(info["rounds"], info["PL"], marker="o", label=f"d={d} (eps={info['epsilon']:.2e})")
plt.yscale("log")
plt.xlabel("rounds n")
plt.ylabel("logical failure P_L(n)")
plt.legend()
plt.grid(True)
plt.show()

# epsilon_d vs d (로그)
ds = sorted(results.keys())
eps = [results[d]["epsilon"] for d in ds]

plt.figure()
plt.plot(ds, eps, marker="o")
plt.yscale("log")
plt.xlabel("distance d")
plt.ylabel("fitted epsilon_d (per round)")
plt.grid(True)
plt.show()

# Λ 비율
def ratio(a,b): return results[a]["epsilon"] / results[b]["epsilon"]
if 3 in results and 5 in results:
    print("Lambda_3/5 =", ratio(3,5))
if 5 in results and 7 in results:
    print("Lambda_5/7 =", ratio(5,7))

