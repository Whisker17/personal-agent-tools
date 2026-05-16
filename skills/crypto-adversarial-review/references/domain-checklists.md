# Domain-Specific Adversarial Checklists

Per-domain checks to apply during adversarial review. Each checklist item specifies the default severity if the issue is found and not already flagged in the report.

## Table of Contents

1. [DeFi Protocols](#defi-protocols)
2. [Tokens and Tokenomics](#tokens-and-tokenomics)
3. [Governance](#governance)
4. [L1/L2 Infrastructure](#l1l2-infrastructure)
5. [Bridges and Cross-Chain](#bridges-and-cross-chain)
6. [Stablecoins](#stablecoins)

---

## DeFi Protocols

### Oracle Dependency
- Single oracle source with no fallback → **critical**
- Oracle update frequency not analyzed relative to protocol's sensitivity → **major**
- No discussion of oracle manipulation risk (e.g., flash loan attacks on TWAP oracles) → **major**
- Oracle trust assumptions not stated → **minor**

### Liquidation Mechanics
- No stress test of liquidation cascades under extreme volatility → **major**
- Bad debt accumulation mechanism not analyzed → **major**
- Liquidation incentive structure not evaluated (are liquidators properly incentivized?) → **minor**

### Composability Risk
- Dependencies on other protocols not mapped → **major**
- No analysis of what happens when a dependency protocol fails, pauses, or upgrades → **major**
- Recursive dependency chains (A depends on B depends on C) not traced → **minor**

### MEV Exposure
- No discussion of front-running, sandwich attacks, or JIT liquidity → **major** for DEXes, **minor** for other protocols
- MEV mitigation measures (if any) not evaluated → **minor**

### Smart Contract Risk
- Audit status not mentioned → **critical**
- Only one audit, no bug bounty program → **major**
- Upgrade mechanisms (proxy patterns, timelocks) not analyzed → **major**
- Admin key concentration (multisig threshold, timelock delays) not discussed → **major**
- No mention of formal verification status for critical math → **minor**

### Economic Attack Vectors
- Flash loan attack surface not considered → **major** for lending/DEX protocols
- Infinite mint / re-entrancy risk not addressed → **critical** if protocol handles token minting
- Sandwich attack profitability not estimated → **minor**

---

## Tokens and Tokenomics

### Supply and Distribution
- Total/max supply not stated or inconsistent with on-chain data → **critical**
- Insider allocation > 30% without documented vesting schedule → **major**
- Missing unlock schedule analysis with dates and amounts → **major**
- No comparison to competitor tokenomics → **minor**
- Treasury size and burn rate not calculated → **minor**

### Value Accrual
- Token utility described but not validated against smart contract logic → **major**
- Revenue sharing / buyback mechanisms claimed but not verified on-chain → **critical**
- Circular value arguments ("token is valuable because people hold it") not flagged → **major**

### Inflation and Dilution
- Emission schedule not modeled forward → **major**
- Impact of emissions on holder dilution not quantified → **minor**
- Staking rewards sourced from inflation not distinguished from protocol revenue → **major**

---

## Governance

### Power Concentration
- Top 10 holders control > 50% voting power and this is not flagged → **critical**
- Delegation patterns not analyzed (delegated power can concentrate governance) → **major**
- No analysis of actual governance participation rates → **major**

### Process and Enforcement
- Off-chain governance with no on-chain enforcement → **major** (should be flagged as a risk)
- Timelock and veto mechanisms not documented → **minor**
- Emergency powers / guardian roles not analyzed → **major**

### Historical Governance Actions
- No review of past governance proposals and outcomes → **minor**
- Controversial or contested proposals not discussed → **major** if they exist

---

## L1/L2 Infrastructure

### Security Model
- Consensus mechanism described but fault tolerance not quantified → **major**
- Validator set size and concentration not analyzed → **major**
- Slashing conditions not documented → **minor**
- Finality guarantees not compared to claims → **major**

### Scalability Claims
- TPS/throughput claims not verified against on-chain data → **major**
- Performance under load (actual vs theoretical max) not distinguished → **major**
- State growth and storage costs not projected → **minor**

### L2-Specific
- Data availability solution not analyzed (rollup vs validium vs optimium) → **major**
- Sequencer centralization risk not discussed → **critical** for L2s with single sequencer
- Escape hatch / forced withdrawal mechanism not documented → **critical**
- Fraud proof / validity proof status (live vs in development) → **critical**

---

## Bridges and Cross-Chain

### Trust Assumptions
- Bridge security model not specified (trusted vs trustless) → **critical**
- Validator/relayer set not analyzed → **major**
- Multisig threshold and key holder identities not documented → **major**

### Historical Security
- Past bridge exploits in the same category not referenced → **major**
- TVL at risk not quantified → **major**

### Failure Modes
- What happens if the bridge goes down? Are funds recoverable? → **critical** if not addressed
- Chain reorganization handling not discussed → **major**

---

## Stablecoins

### Peg Mechanism
- Peg maintenance mechanism not explained in detail → **critical**
- Historical depeg events not analyzed → **major**
- Redemption mechanism and delays not documented → **major**

### Collateral
- Collateral composition not broken down with percentages → **major**
- Collateral quality (on-chain vs off-chain, liquid vs illiquid) not assessed → **major**
- Attestation/audit frequency for off-chain reserves → **major** for fiat-backed
- Collateral ratio under stress not modeled → **major** for over-collateralized

### Regulatory Risk
- Regulatory classification and jurisdictional risks not discussed → **major**
- Issuer compliance and licensing status not mentioned → **minor**
