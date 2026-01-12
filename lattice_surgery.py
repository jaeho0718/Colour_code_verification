import numpy as np
import matplotlib.pyplot as plt

def run_monte_carlo_simulation():
    # --- 1. 양자 엔진 (정확한 확률 계산용) ---
    I = np.eye(2, dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    H = (1/np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)
    P0 = np.array([[1, 0], [0, 0]], dtype=complex) # |0><0|
    P1 = np.array([[0, 0], [0, 1]], dtype=complex) # |1><1|

    # 텐서곱 헬퍼
    def kron(*args):
        res = args[0]
        for op in args[1:]:
            res = np.kron(res, op)
        return res

    # 노이즈 주입 (Depolarizing Noise)
    def apply_noise_1q(rho, qubit_idx, p, n_qubits=3):
        if p == 0: return rho
        ops = [X, Y, Z]
        rho_new = (1 - p) * rho
        for op in ops:
            op_list = [I] * n_qubits
            op_list[qubit_idx] = op
            full_op = kron(*op_list)
            rho_new += (p / 3) * (full_op @ rho @ full_op.conj().T)
        return rho_new

    # 정확한 이론적 Fidelity 계산 (기존 로직)
    def get_exact_fidelity(input_label, noise_p):
        ket0 = np.array([[1], [0]])
        ket1 = np.array([[0], [1]])
        if input_label == '0': psi = ket0
        elif input_label == '1': psi = ket1
        elif input_label == '+': psi = (ket0 + ket1)/np.sqrt(2)
        elif input_label == '-': psi = (ket0 - ket1)/np.sqrt(2)
        
        # Init State: |psi>_L1 |0>_L2 |0>_Anc
        state_vec = kron(psi, ket0, ket0)
        rho = state_vec @ state_vec.conj().T

        # Circuit Execution
        op_h = kron(I, I, H)
        rho = apply_noise_1q(op_h @ rho @ op_h.conj().T, 2, noise_p)

        # CNOT Anc->L1
        cx1 = kron(I, I, P0) + kron(X, I, P1)
        rho = apply_noise_1q(cx1 @ rho @ cx1.conj().T, 0, noise_p)
        rho = apply_noise_1q(rho, 2, noise_p)

        # CNOT Anc->L2
        cx2 = kron(I, I, P0) + kron(I, X, P1)
        rho = apply_noise_1q(cx2 @ rho @ cx2.conj().T, 1, noise_p)
        rho = apply_noise_1q(rho, 2, noise_p)

        # H on Anc
        rho = apply_noise_1q(op_h @ rho @ op_h.conj().T, 2, noise_p)

        # Measurement & Correction Logic
        final_rho_L2 = np.zeros((2,2), dtype=complex)
        for m1 in [0, 1]:
            for m2 in [0, 1]:
                proj = kron(P0 if m2==0 else P1, I, P0 if m1==0 else P1)
                unnorm_rho = proj @ rho @ proj.conj().T
                prob = np.trace(unnorm_rho).real
                if prob < 1e-15: continue
                post_rho = unnorm_rho / prob
                
                corr_op = I
                if m1 == 1: corr_op = Z @ corr_op
                if m2 == 1: corr_op = X @ corr_op
                full_corr = kron(I, corr_op, I)
                corrected_rho = full_corr @ post_rho @ full_corr.conj().T
                
                rho_tensor = corrected_rho.reshape((2,2,2, 2,2,2))
                rho_L2 = np.einsum('ijkilm->jl', rho_tensor)
                final_rho_L2 += prob * rho_L2

        target_vec = psi
        target_rho = target_vec @ target_vec.conj().T
        return np.trace(target_rho @ final_rho_L2).real

    # --- 2. 몬테카를로 샘플링 (핵심 수정 부분) ---
    def get_sampled_fidelity(exact_fid, shots=5000):
        """
        정확한 확률(exact_fid)을 기반으로, 지정된 횟수(shots)만큼 
        동전을 던지는 시뮬레이션을 수행하여 랜덤한 결과값을 반환합니다.
        """
        # 이항 분포(Binomial)에서 샘플링: n번 던져서 성공한 횟수
        success_count = np.random.binomial(n=shots, p=exact_fid)
        return success_count / shots

    # --- 3. 실행 및 시각화 ---
    labels = [r'$|0_L\rangle$', r'$|1_L\rangle$', r'$|+_L\rangle$', r'$|-_L\rangle$']
    states = ['0', '1', '+', '-']
    shots = 5000  # 샷 수 (이 값을 바꾸면 흔들리는 정도가 바뀜)

    # 노이즈 파라미터 (논문 재현용)
    p_exp_Z = 0.045
    p_exp_X = 0.035
    p_sim = 0.030

    print(f">>> Running Monte Carlo Simulation (Shots={shots})...")
    
    # Measured 데이터 생성 (랜덤성 추가됨)
    measured_fids = []
    measured_fids.append(get_sampled_fidelity(get_exact_fidelity('0', p_exp_Z), shots))
    measured_fids.append(get_sampled_fidelity(get_exact_fidelity('1', p_exp_Z+0.005), shots))
    measured_fids.append(get_sampled_fidelity(get_exact_fidelity('+', p_exp_X), shots))
    measured_fids.append(get_sampled_fidelity(get_exact_fidelity('-', p_exp_X), shots))

    # Simulated 데이터 (기준선이므로 정확한 값 사용)
    sim_fids = [get_exact_fidelity(s, p_sim) for s in states]

    # 그래프 그리기
    fig, ax = plt.subplots(figsize=(6, 5))
    x = np.arange(len(labels))
    width = 0.65

    # Simulated (Wireframe)
    ax.bar(x, sim_fids, width, color='white', edgecolor='black', linewidth=1.5, label='Simulated', zorder=2)
    # Measured (Gold Filled) - 이제 매번 높이가 조금씩 다릅니다
    ax.bar(x, measured_fids, width * 0.9, color='#F1C232', alpha=1.0, label='Measured (Monte Carlo)', zorder=3)
    # Ideal Line
    ax.hlines(1.0, -0.5, 3.5, colors='gray', linestyles='dotted', label='Ideal')

    ax.set_ylim(0.7, 1.02)
    ax.set_ylabel(r'State fidelity, $F$', fontsize=14)
    ax.set_title(f'Teleported State Fidelity (Shots={shots})', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=13)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.tick_params(direction='in', top=True, right=True)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3, frameon=False, fontsize=11)
    
    plt.tight_layout()
    plt.show()
    
    print("\n[Result Summary - 매번 값이 달라집니다]")
    print(f"Measured (Random): {[round(f, 4) for f in measured_fids]}")
    print(f"Simulated (Exact): {[round(f, 4) for f in sim_fids]}")

if __name__ == "__main__":
    run_monte_carlo_simulation()
