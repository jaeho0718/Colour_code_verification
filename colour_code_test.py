import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

# =========================================================
# 1. 노이즈 모델 설정 (Magic State 전용)
# =========================================================
# 실제 양자 컴퓨터와 유사한 에러 환경 조성
nm_magic = NoiseModel()
# 1-qubit 게이트 에러 (0.5%)
nm_magic.add_all_qubit_quantum_error(depolarizing_error(0.005, 1), ['id', 'rz', 'sx', 'x', 'h', 'ry', 'measure'])
# 2-qubit 게이트 에러 (1.0% - CNOT이 더 에러가 큼)
nm_magic.add_all_qubit_quantum_error(depolarizing_error(0.01, 2), ['cx'])

sim_magic = AerSimulator(noise_model=nm_magic)

print(">>> Running Magic State Injection Simulation...")

# =========================================================
# 2. 시뮬레이션 로직 (Real Circuit Execution)
# =========================================================
def run_magic_sim():
    # 7-qubit Steane Code 기반 Magic State Injection 회로
    qc = QuantumCircuit(7)
    
    # [Injection] 초기 불완전한 Magic State 준비
    qc.ry(np.pi/4, 0) 
    
    # [Encoding] 에러 정정 부호로 인코딩 (Entanglement)
    qc.h(1); qc.h(2); qc.h(3)
    qc.cx(1,0); qc.cx(2,0); qc.cx(3,0) 
    qc.cx(0,4); qc.cx(0,5); qc.cx(0,6)
    qc.cx(1,4); qc.cx(2,5); qc.cx(3,6)
    
    qc.barrier() # 시각적 분리 (여기서 노이즈가 주로 작용한다고 가정)
    
    # Noise가 섞이는 구간 (Identity gate로 시간 경과 표현)
    for i in range(7): qc.id(i)
    
    # [Decoding & Verification]
    qc.cx(3,6); qc.cx(2,5); qc.cx(1,4)
    qc.cx(0,4); qc.cx(0,5); qc.cx(0,6)
    qc.cx(1,0); qc.cx(2,0); qc.cx(3,0)
    qc.h(1); qc.h(2); qc.h(3)
    
    # 검증을 위한 역연산
    qc.ry(-np.pi/4, 0) 
    
    qc.measure_all()
    
    # 시뮬레이션 실행 (5000번 반복)
    res = sim_magic.run(transpile(qc, sim_magic), shots=5000).result()
    counts = res.get_counts()
    
    # [Post-selection Logic] 데이터 분석
    total = 0; raw_ok = 0; ps_ok = 0; kept = 0
    
    for outcome, count in counts.items():
        clean = outcome.replace(" ", "")
        syn = clean[:-1]  # Syndrome bits (에러 감지용)
        dat = clean[-1]   # Data bit (실제 결과)
        
        total += count
        
        # 1. Raw Fidelity: 아무 처리 안 했을 때 정답('0')일 확률
        if dat == '0': raw_ok += count
        
        # 2. Post-selected Fidelity: 신드롬이 '0'(에러 없음)일 때만 데이터를 채택
        if int(syn) == 0: 
            kept += count
            if dat == '0': ps_ok += count
            
    # 결과 반환 (Raw 정확도, 증류된 정확도)
    return raw_ok/total, ps_ok/kept

# =========================================================
# 3. 결과 플로팅 (단독 그래프)
# =========================================================
raw_fid, ps_fid = run_magic_sim()

plt.figure(figsize=(6, 5))
bars = plt.bar(['Raw', 'Post-selected'], [raw_fid, ps_fid], color=['gray', 'blue'])

plt.ylim(0.8, 1.02) # 차이를 잘 보여주기 위한 Y축 설정
plt.title("Sec 6. Magic State Injection Fidelity", fontsize=12, fontweight='bold')
plt.ylabel("State Fidelity", fontsize=11)

# 목표치 라인 (Target)
plt.axhline(0.99, color='green', linestyle='--', label='Target > 0.99')

# 막대 위에 수치 표시
for bar in bars:
    val = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, val, f"{val:.4f}", 
             ha='center', va='bottom', fontweight='bold', fontsize=11)

plt.legend(loc='lower left')
plt.tight_layout()
plt.show()
