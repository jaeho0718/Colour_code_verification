# Scaling and Logic in the Colour Code on a Superconducting Quantum Processor

### 1-1. Why quantum error correction?

Quantum information is extremely fragile: small noise can destroy the computation.

**Quantum error correction (QEC)** protects information by spreading one logical qubit across many physical qubits, so that local errors can be detected and corrected.

---

### 1-2. What is the colour code? (VS Surface Code)

![image.png](%ED%8F%AC%EC%8A%A4%ED%84%B0%20%EC%9E%91%EC%84%B1/image.png)

![image.png](%ED%8F%AC%EC%8A%A4%ED%84%B0%20%EC%9E%91%EC%84%B1/image%201.png)

![image.png](%ED%8F%AC%EC%8A%A4%ED%84%B0%20%EC%9E%91%EC%84%B1/image%202.png)

![image.png](%ED%8F%AC%EC%8A%A4%ED%84%B0%20%EC%9E%91%EC%84%B1/image%203.png)

The **colour code** is a *topological* quantum error-correcting code.

- This work demonstrates a **distance-5 colour code**, meaning multiple physical errors are needed before a logical error occurs.

|  | Colour Code | Surface Code |
| --- | --- | --- |
| **Lattice Structure** | Hexagonal/Triangular lattice (Honeycomb) | Square lattice (Chessboard pattern) |
| Transversal Clifford Gates | **Fully possible** (self-dual property) | Partially possible |
| Error Threshold | **Relatively lower**(complex syndrome extraction) | Relatively higher |
| Data Qubits (d=5﻿) | 19 qubits | 25 qubits |
| Syndrome Weight | **Weight-6** (hexagons) & **Weight-4** (boundaries) | Mostly **Weight-4** |
| Hardware Connectivity | Complex, but optimized via **Superdense layout** | Native to standard square grids |

---

### 1-3. What are Clifford gates?

**Clifford gates** (e.g. X, Z, H, S) are a special class of quantum operations that:

$UPU†∈{±X,±Y,±Z}\ for\ all\ P∈{X,Y,Z}$

---

### 1-4. Why Clifford gates are not enough

**Universal Computation Gap:** Clifford gates are fault-tolerant but not universal, as they are classically simulatable. To achieve quantum advantage, **non-Clifford operations** (e.g. $T-gates$) must be introduced indirectly via **Magic State Injection**.

---

**Why Quantum Error Correction (QEC)?**
• **Problem:** Quantum states are fragile; noise easily destroys computation.
• **Solution:** QEC encodes one **logical qubit** across multiple **physical qubits**.
• **Mechanism:** Detects and corrects local errors without collapsing the logical information.

**Color Code vs Surface Code**

![image.png](%ED%8F%AC%EC%8A%A4%ED%84%B0%20%EC%9E%91%EC%84%B1/image%204.png)

**Color Code** is a topological code featuring **transversal gates**, crucial for fault tolerance. This work utilizes a **Distance-5 (d=5)** code.

---

---

아키텍처 및 매핑 

![image.png](%ED%8F%AC%EC%8A%A4%ED%84%B0%20%EC%9E%91%EC%84%B1/image%205.png)

Google maps the triangular colour code onto Willow’s square grid with a **superdense layout** that places data and X/Z ancilla qubits so all required couplings are nearest-neighbour (Fig. 1a). They then **swap selected data/ancilla roles** to match Willow’s readout-line constraint, ensuring each line contains **only data or only ancillas** (Fig. 1c–d).

### **3. Distance Scaling & Error Analysis**

![image.png](%ED%8F%AC%EC%8A%A4%ED%84%B0%20%EC%9E%91%EC%84%B1/image%206.png)

![image.png](%ED%8F%AC%EC%8A%A4%ED%84%B0%20%EC%9E%91%EC%84%B1/image%207.png)

Increasing the code distance from $d=3$  to $d=5$ reduces the per-cycle logical error rate from about 1.71% to 1.10%, demonstrating scalable error suppression. The error suppression factor$Λ=ε3/ε5$=1.56(4) confirms operation below the fault-tolerance threshold. An error budget analysis shows that two-qubit CZ gates dominate the total error (~39%), making their improvement the key path forward.

---

1. Benchmarking 

![스크린샷 2026-01-12 173722.png](%ED%8F%AC%EC%8A%A4%ED%84%B0%20%EC%9E%91%EC%84%B1/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7_2026-01-12_173722.png)

**Logical randomized benchmarking(LRB)** evaluates how accurately the system executes logical commands, measuring the average error of **transversal Clifford operations.**

Via **Interleaved Randomized Benchmarking(IRB)**, the total error rate during the sequence was approximately **1.98%**, sum of **baseline system error of 1.71%** and an **additional gate error of 0.27%**. -> The specific gate error (0.27%) is significantly lower than the intrinsic system error (1.71%) : The **transversal single-qubit gates** are highly efficient and impose minimal overhead on the logical state.

---

1. **Decoding Algorithm**

![image.png](%ED%8F%AC%EC%8A%A4%ED%84%B0%20%EC%9E%91%EC%84%B1/35ef3da8-a56a-4644-889a-6e68df7849a8.png)

|  | **Relative Speed** | Λ₃/₅ |
| --- | --- | --- |
| **Chromobius** | 1× (baseline) | 0.83 - 0.93 |
| **MLE** | ~3× | **1.56**  |
| **AlphaQubit** | ~880× | 1.35 - 1.53 |

In color codes, the hyper-edge structure where a single physical error simultaneously activates three syndromes causes the combinatorial complexity of MWPM-based decoding to grow exponentially. To address this issue, three decoders were compared: **Chromobius** (graph decomposition), **MLE** (mixed-integer linear programming), and **AlphaQubit** (recurrent neural network).

---

1. **Generation of High-Fidelity Magic States via Post-Selection**
    
    ![image.png](%ED%8F%AC%EC%8A%A4%ED%84%B0%20%EC%9E%91%EC%84%B1/image%208.png)
    
    We implemented an efficient injection protocol to generate magic states ($|A_L\rangle$) for universal quantum computation by leveraging the transversal properties of the color code. To mitigate physical errors during the expansion from a single physical qubit to a distance-3 logical qubit, we applied a post-selection technique based on stabilizer measurements. Discarding approximately 25% of the data where errors were detected significantly reduced the average infidelity from 3.9% to 0.085%, achieving a state fidelity of 99.915%. This result surpasses the threshold required for magic state distillation, successfully demonstrating a practical and high-fidelity magic state injection on a superconducting processor.
    
    ![image.png](%ED%8F%AC%EC%8A%A4%ED%84%B0%20%EC%9E%91%EC%84%B1/image%209.png)
    

---

Logical two-qubit operations are not implemented by directly applying physical two-qubit gates between logical qubits. Instead, they are realized through **lattice surgery:**

1. merging two separate logical qubits into one single patch 
2. and then pulling them apart

by entangling two logical qubits to combine them into a single logical patch, transferring information from one logical qubit to the other, and then separate.

![ColorCode3_Diagram.width-1250.png](%ED%8F%AC%EC%8A%A4%ED%84%B0%20%EC%9E%91%EC%84%B1/ColorCode3_Diagram.width-1250.png)

**1. Merge**

Initially, the two logical qubits are encoded in separate patches and are unentangled. Then the two patches are brought together and treated as a single larger patch by **redefining the stabilizers along their shared boundary.** This introduces new **joint stabilizer measurements** that span both logical qubits. As a result, the two logical qubits become entangled.

**2. Split**

After the joint stabilizer measurements are completed, the merged patch is separated back into two independent logical patches. But the information obtained during the merge step is retained. This can be done by applying appropriate **Pauli frame updates.**

![image.png](%ED%8F%AC%EC%8A%A4%ED%84%B0%20%EC%9E%91%EC%84%B1/image%2010.png)

추가

![image.png](%ED%8F%AC%EC%8A%A4%ED%84%B0%20%EC%9E%91%EC%84%B1/image%2011.png)

### **fig. 1 | Distance scaling beyond the experimental regime.**

Simulated logical failure probability $P_L(n)$ of the triangular colour code for $d=3,5,7$.

Solid lines show fits used to extract the per-round logical error rate  $εd.$

The monotonic decrease of  $εd$  with distance demonstrates continued exponential suppression of logical errors beyond the experimentally studied code sizes.

![1000007167.png](%ED%8F%AC%EC%8A%A4%ED%84%B0%20%EC%9E%91%EC%84%B1/1000007167.png)

**Fig 2.** Fig 2 presents simulation results for magic state injection using the 7-qubit Steane code. While the fidelity remained around 0.94 without post-selection, it surpassed the target threshold of 0.99 upon application, demonstrating that post-selection is essential for generating high-quality states.

![image.png](%ED%8F%AC%EC%8A%A4%ED%84%B0%20%EC%9E%91%EC%84%B1/image%2012.png)

**Fig 3.** Fig 3 evaluates the performance of quantum teleportation in a noisy environment via 5,000 Monte Carlo simulations. Despite incorporating realistic hardware-level noise, the fidelity remained above 0.90 across all logical basis states, verifying the stability of the protocol.


## Conclusion
This study experimentally demonstrates logical error suppression in the colour code by scaling code distance ($\Lambda_{3/5}=1.56(4)$) on a 72-qubit superconducting processor, alongside efficient logical operations using transversal gates and lattice surgery. While magic state injection achieved fidelities exceeding 99% with post-selection, establishing a path for universal computation, the performance currently falls short of the surface code ($\Lambda \approx 2.31$) due to complex stabilizer measurements. Simulations indicate the colour code can surpass the surface code in efficiency with a fourfold improvement in physical error rates. Future research must prioritize reducing CZ gate errors, which account for 39% of the error budget, and advancing decoding speeds.