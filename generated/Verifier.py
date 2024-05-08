# Code automatically generated - DO NOT EDIT.

import typing

import algopy as py
from algopy import subroutine, BigUInt, Bytes, arc4, UInt64, urange
from algopy.arc4 import UInt256, abimethod, Tuple, DynamicArray, StaticArray, String
from algopy.op import sha256, EllipticCurve as ec, EC

Bytes32: typing.TypeAlias = StaticArray[arc4.Byte, typing.Literal[32]]

#################### Curve parameters ####################

# curve order
R_MOD = 21888242871839275222246405745257275088548364400416034343698204186575808495617

# field order
P_MOD = 21888242871839275222246405745257275088696311157297823662689037894645226208583

#################### Trusted setup ####################

G2_SRS_0_X_0 = 11559732032986387107991004021392285783925812861821192530917403151452391805634
G2_SRS_0_X_1 = 10857046999023057135944570762232829481370756359578518086990519993285655852781
G2_SRS_0_Y_0 = 4082367875863433681332203403145435568316851327593401208105741076214120093531
G2_SRS_0_Y_1 = 8495653923123431417604973247489272438418190587263600148770280649306958101930

G2_SRS_1_X_0 = 17231025384763736816414546592865244497437017442647097510447326538965263639101
G2_SRS_1_X_1 = 21831381940315734285607113342023901060522397560371972897001948545212302161822
G2_SRS_1_Y_0 = 11507326595632554467052522095592665270651932854513688777769618397986436103170
G2_SRS_1_Y_1 = 2388026358213174446665280700919698872609886601280537296205114254867301080648

G1_SRS_X = 1
G1_SRS_Y = 2

######################################################

class Verifier(py.ARC4Contract):
	@abimethod(create='require')
	def create(self, name: String) -> None:
		"""On creation, save application name in global state"""
		self.app_name = name
		self.immutable = False

	@abimethod(allow_actions=["UpdateApplication", "DeleteApplication"])
	def update(self) -> None:
		"""Creator can update and delete the application if the immutable
		   property is false."""
		assert not self.immutable
		assert py.Global.creator_address == py.Txn.sender

	@abimethod
	def make_immutable(self) -> None:
		"""Creator can make the contract immutable."""
		assert py.Global.creator_address == py.Txn.sender
		self.immutable = True

	@abimethod
	def verify(self,
	           proof: DynamicArray[Bytes32],
			   public_inputs: DynamicArray[Bytes32],
			   ) -> arc4.Bool:
		"""Verify the proof for the given public inputs.
		   Return a boolean indicating whether the proof is valid"""

		q = BigUInt(R_MOD)

		# check proof and public inputs lengths
		assert proof.length == 26
		assert public_inputs.length == 1

		# Read verifying key
		VK_NB_PUBLIC_INPUTS = UInt64(1)
		VK_DOMAIN_SIZE = BigUInt(512)
		VK_INV_DOMAIN_SIZE = BigUInt(21845492397480214137827955734036069473141043376196471776620668631523902619649)
		VK_OMEGA = BigUInt(6837567842312086091520287814181175430087169027974246751610506942214842701774)

		VK_QL = Bytes.from_hex("305c147b6a09d2f7e2acdf861851b8ac623d25a75597d35ba3735a58e67c9f6f129928ef2bb2e2ce54ab6eda80aaf95f7d245d51ef945fe69f40064aca3bd402")
		VK_QR = Bytes.from_hex("2f68cd6b764d1e653371272e3046a2558ab38ce37ecbc054bb7df37c31ee26392311d17830aa7d8795967086c0e4d4597d122176edce571c33a72b9773389396")
		VK_QO = Bytes.from_hex("08d5e3211945e1064d319efc2aa9e80e349a8f52a79f0b5e0195d3b7051e3fd22839c621b767b84833009f879b41d5ed786b90c6fb7929bd917d2b958db887d2")
		VK_QM = Bytes.from_hex("1128d08f95967307ad395ce4e44be3e47b2b9c7f45de968b8c9d16bb2241cde2163c009aa8e38add58f57744e9cf748aa76eef80927d07f919653581ef52a9be")
		VK_QK = Bytes.from_hex("19fb4308d898dd03703da497566a1dfb167c0bb51a854be87c89d6d4be95a5ed02fb415e2059d31a2224f79f5069199ef99d9c40f39bfe8324aacfd438e26fbd")

		VK_S1 = Bytes.from_hex("2c470ee98067e88a6f598fcf466dbb1347c6d37fd29469d58f56148f3b771d1a2231c4c19478ed72b24e62019543668746651759eeeb234b68a11a1273c12f4b")
		VK_S2 = Bytes.from_hex("13ef02390af37d851ece9a4f8b7705561a389681f3c380aef62cd9ff497ceb3412aac6955b0319626cb853ea937cbfd126047033302308758baa301c17d30775")
		VK_S3 = Bytes.from_hex("1dc0f72e11743f4de272e2472f5442c2a877f9e42590c09639f5f248a761bb0623867e6560f209589bce52cbd0cc8fd5f943df4411c1428e804736f3527083c5")
		
		VK_COSET_SHIFT = BigUInt(5)

		# Read proof #
		# wires commitments
		L_COM = proof[0].bytes + proof[1].bytes
		R_COM = proof[2].bytes + proof[3].bytes
		O_COM = proof[4].bytes + proof[5].bytes

		# h = h_0 + x^{n+2}h_1 + x^{2(n+2)}h_
		H_0 = proof[6].bytes + proof[7].bytes
		H_1 = proof[8].bytes + proof[9].bytes
		H_2 = proof[10].bytes + proof[11].bytes

		# wire values at zeta
		L_AT_Z = proof[12].copy()
		R_AT_Z = proof[13].copy()
		O_AT_Z = proof[14].copy()

		S1_AT_Z = proof[15].copy() 						  # s1(zeta)
		S2_AT_Z = proof[16].copy() 						  # s2(zeta)
		GRAND_PRODUCT = proof[17].bytes + proof[18].bytes # z(x)
		GRAND_PRODUCT_AT_Z_OMEGA = proof[19].copy()       # z(w*zeta)
		QUOTIENT_POLY_AT_Z = proof[20].copy()             # t(zeta)
		LINEAR_POLY_AT_Z = proof[21].copy()               # r(zeta)

		# Folded proof for opening of H, linear poly, l, r, o, s1, s2, qc
		BATCH_OPENING_AT_Z = proof[22].bytes + proof[23].bytes
		OPENING_AT_Z_OMEGA = proof[24].bytes + proof[25].bytes

		### check proof public inputs are well-formed ###
		if (BigUInt.from_bytes(L_AT_Z.bytes) >= q
				or BigUInt.from_bytes(R_AT_Z.bytes) >= q
				or BigUInt.from_bytes(O_AT_Z.bytes) >= q
				or BigUInt.from_bytes(S1_AT_Z.bytes) >= q
				or BigUInt.from_bytes(S2_AT_Z.bytes) >= q
				or BigUInt.from_bytes(GRAND_PRODUCT_AT_Z_OMEGA.bytes) >= q
				or BigUInt.from_bytes(QUOTIENT_POLY_AT_Z.bytes) >= q
				or BigUInt.from_bytes(LINEAR_POLY_AT_Z.bytes) >= q):
			return arc4.Bool(False)

		for i in urange(public_inputs.length):
			if BigUInt.from_bytes(public_inputs[i].bytes) >= q:
				return arc4.Bool(False)

		### Verify the proof ###

		# Compute the fiat-shamir challenges as the prover (gnark).
		# After deriving all challenges, we need to make them modulo R_MOD.

		public_inputs_bytes = Bytes(b'')
		for i in urange(public_inputs.length):
			public_inputs_bytes += public_inputs[i].bytes

		gamma_pre = sha256(b'gamma' + VK_S1 + VK_S2 + VK_S3 + VK_QL + VK_QR + VK_QM + VK_QO + VK_QK
						   + public_inputs_bytes + L_COM + R_COM + O_COM)
		beta_pre = sha256(b'beta' + gamma_pre)
		alpha_pre = sha256(b'alpha' + beta_pre + GRAND_PRODUCT)
		zeta_pre = sha256(b'zeta' + alpha_pre + H_0 + H_1 + H_2)

		gamma = curvemod(gamma_pre)
		beta = curvemod(beta_pre)
		alpha = curvemod(alpha_pre)
		zeta = curvemod(zeta_pre)

		# Zz is eval of Xⁿ-1 at zeta
		Zz = (expmod(zeta, VK_DOMAIN_SIZE, q) + q - BigUInt(1)) % q

		# zn is Zz * 1/n
		zn = (Zz * VK_INV_DOMAIN_SIZE) % q

		# Let's prepare to interpolate the public inputs
		w_ = BigUInt(1)
		batch = DynamicArray[UInt256]()
		for i in urange(VK_NB_PUBLIC_INPUTS):
			x = (zeta + q - w_) % q
			batch.append(UInt256(x))
			w_ = (w_ * VK_OMEGA) % q

		# Compute batch inversion
		temp = DynamicArray[UInt256]()
		prev = BigUInt(1)
		temp.append(UInt256(prev))
		for x256 in batch:
			x = BigUInt.from_bytes(x256.bytes)
			y = (x * prev) % q
			temp.append(UInt256(y))
			prev = y
		inv = expmod(prev, q - BigUInt(2), q)
		i = VK_NB_PUBLIC_INPUTS
		while i > 0:
			tmp = BigUInt.from_bytes(batch[i-1].bytes)
			cur = (inv * BigUInt.from_bytes(temp[i-1].bytes)) % q
			batch[i-1] = UInt256(cur)
			inv = (inv * tmp) % q
			i -= 1

		# We can now interpolate the public inputs (PI)
		w_ = BigUInt(1)
		for i in urange(VK_NB_PUBLIC_INPUTS):
			batch[i] = UInt256((w_ * ((BigUInt.from_bytes(batch[i].bytes) * zn)
								% q)) % q)
			w_ = (w_ * VK_OMEGA) % q

		tmp = BigUInt(0)
		PI = BigUInt(0)
		for i in urange(VK_NB_PUBLIC_INPUTS):
			tmp = (BigUInt.from_bytes(batch[i].bytes)
				   * BigUInt.from_bytes(public_inputs[i].bytes)) % q
			PI = (PI + tmp) % q

		# compute alpha2Lagrange: alpha**2 * (z**n - 1) / (z - 1)
		res = (zeta + q - BigUInt(1)) % q
		res = expmod(res, q - BigUInt(2), q)
		res = (res * zn) % q
		res = (res * alpha) % q
		res = (res * alpha) % q
		alpha2Lagrange = res

		# verify quotient polynomial evaluation at zeta
		s1 = (BigUInt.from_bytes(S1_AT_Z.bytes) * beta) % q
		s1 = (s1 + gamma + BigUInt.from_bytes(L_AT_Z.bytes)) % q

		s2 = (BigUInt.from_bytes(S2_AT_Z.bytes) * beta) % q
		s2 = (s2 + gamma + BigUInt.from_bytes(R_AT_Z.bytes)) % q

		o = (BigUInt.from_bytes(O_AT_Z.bytes) + gamma) % q

		s1 = (s1 * s2) % q
		s1 = (s1 * o) % q
		s1 = (s1 * alpha) % q
		s1 = (s1 * BigUInt.from_bytes(GRAND_PRODUCT_AT_Z_OMEGA.bytes)) % q

		quot = (BigUInt.from_bytes(LINEAR_POLY_AT_Z.bytes) + PI + s1 + q
								   - alpha2Lagrange) % q

		s2 = (BigUInt.from_bytes(QUOTIENT_POLY_AT_Z.bytes) * Zz) % q

		if quot != s2:
			return arc4.Bool(False)

		# compute the folded commitment to H
		n2 = VK_DOMAIN_SIZE + BigUInt(2)
		zn2 = expmod(zeta, n2, q)
		folded_h = ec.scalar_mul(EC.BN254g1, H_2, zn2.bytes)
		folded_h = ec.add(EC.BN254g1, folded_h, H_1)
		folded_h = ec.scalar_mul(EC.BN254g1, folded_h, zn2.bytes)
		folded_h = ec.add(EC.BN254g1, folded_h, H_0)

		# compute commitment to linearization polynomial
		u = (BigUInt.from_bytes(GRAND_PRODUCT_AT_Z_OMEGA.bytes) * beta) % q
		v = (BigUInt.from_bytes(S1_AT_Z.bytes) * beta) % q
		v = (v + BigUInt.from_bytes(L_AT_Z.bytes) + gamma) % q
		w  = (BigUInt.from_bytes(S2_AT_Z.bytes) * beta) % q
		w = (w + BigUInt.from_bytes(R_AT_Z.bytes) + gamma) % q

		s1 = (u * v) % q
		s1 = (s1 * w) % q
		s1 = (s1 * alpha) % q

		coset_square = (VK_COSET_SHIFT * VK_COSET_SHIFT) % q
		betazeta = (beta * zeta) % q
		u = (betazeta + BigUInt.from_bytes(L_AT_Z.bytes) + gamma) % q

		v = (betazeta * VK_COSET_SHIFT) % q
		v = (v + BigUInt.from_bytes(R_AT_Z.bytes) + gamma) % q

		w = (betazeta * coset_square) % q
		w = (w + BigUInt.from_bytes(O_AT_Z.bytes) + gamma) % q

		s2 = (u * v) % q
		s2 = q - ((s2 * w) % q)
		s2 = (s2 * alpha + alpha2Lagrange) % q

		lin_poly_com = ec.scalar_mul(EC.BN254g1, VK_QL, L_AT_Z.bytes)

		add_term = ec.scalar_mul(EC.BN254g1, VK_QR, R_AT_Z.bytes)
		lin_poly_com = ec.add(EC.BN254g1, lin_poly_com, add_term)

		add_term = ec.scalar_mul(EC.BN254g1, VK_QO, O_AT_Z.bytes)
		lin_poly_com = ec.add(EC.BN254g1, lin_poly_com, add_term)

		ab = (BigUInt.from_bytes(L_AT_Z.bytes) * BigUInt.from_bytes(R_AT_Z.bytes)) % q
		add_term = ec.scalar_mul(EC.BN254g1, VK_QM, ab.bytes)
		lin_poly_com = ec.add(EC.BN254g1, lin_poly_com, add_term)
		lin_poly_com = ec.add(EC.BN254g1, lin_poly_com, VK_QK)

		add_term = ec.scalar_mul(EC.BN254g1, VK_S3, s1.bytes)
		lin_poly_com = ec.add(EC.BN254g1, lin_poly_com, add_term)

		add_term = ec.scalar_mul(EC.BN254g1, GRAND_PRODUCT, s2.bytes)
		lin_poly_com = ec.add(EC.BN254g1, lin_poly_com, add_term)

		# generate challenge to fold the opening proofs
		r_pre = sha256(b'gamma' + UInt256(zeta).bytes + folded_h + lin_poly_com
			 + L_COM + R_COM + O_COM + VK_S1 + VK_S2 + QUOTIENT_POLY_AT_Z.bytes
			 + LINEAR_POLY_AT_Z.bytes + L_AT_Z.bytes + R_AT_Z.bytes
			 + O_AT_Z.bytes + S1_AT_Z.bytes + S2_AT_Z.bytes
			 + GRAND_PRODUCT_AT_Z_OMEGA.bytes)
		r = curvemod(r_pre)
		r_acc = r

		# fold the proof in one point
		digest = folded_h
		add_term = ec.scalar_mul(EC.BN254g1, lin_poly_com, r_acc.bytes)
		digest = ec.add(EC.BN254g1, digest, add_term)
		claims = (BigUInt.from_bytes(QUOTIENT_POLY_AT_Z.bytes)
				  + (BigUInt.from_bytes(LINEAR_POLY_AT_Z.bytes) * r_acc)
				 ) % q

		r_acc = (r_acc * r) % q
		add_term = ec.scalar_mul(EC.BN254g1, L_COM, r_acc.bytes)
		digest = ec.add(EC.BN254g1, digest, add_term)
		claims = (claims + (BigUInt.from_bytes(L_AT_Z.bytes) * r_acc)) % q

		r_acc = (r_acc * r) % q
		add_term = ec.scalar_mul(EC.BN254g1, R_COM, r_acc.bytes)
		digest = ec.add(EC.BN254g1, digest, add_term)
		claims = (claims + (BigUInt.from_bytes(R_AT_Z.bytes) * r_acc)) % q

		r_acc = (r_acc * r) % q
		add_term = ec.scalar_mul(EC.BN254g1, O_COM, r_acc.bytes)
		digest = ec.add(EC.BN254g1, digest, add_term)
		claims = (claims + (BigUInt.from_bytes(O_AT_Z.bytes) * r_acc)) % q

		r_acc = (r_acc * r) % q
		add_term = ec.scalar_mul(EC.BN254g1, VK_S1, r_acc.bytes)
		digest = ec.add(EC.BN254g1, digest, add_term)
		claims = (claims + (BigUInt.from_bytes(S1_AT_Z.bytes) * r_acc)) % q

		r_acc = (r_acc * r) % q
		add_term = ec.scalar_mul(EC.BN254g1, VK_S2, r_acc.bytes)
		digest = ec.add(EC.BN254g1, digest, add_term)
		claims = (claims + (BigUInt.from_bytes(S2_AT_Z.bytes) * r_acc)) % q

		# verify the folded proof
		r_pre = sha256(digest + BATCH_OPENING_AT_Z + GRAND_PRODUCT + OPENING_AT_Z_OMEGA + UInt256(zeta).bytes + UInt256(r).bytes)
		r = curvemod(r_pre)

		quotient = BATCH_OPENING_AT_Z
		add_term = ec.scalar_mul(EC.BN254g1, OPENING_AT_Z_OMEGA, r.bytes)
		quotient = ec.add(EC.BN254g1, quotient, add_term)

		add_term = ec.scalar_mul(EC.BN254g1, GRAND_PRODUCT, r.bytes)
		digest = ec.add(EC.BN254g1, digest, add_term)

		claims = (claims + (BigUInt.from_bytes(GRAND_PRODUCT_AT_Z_OMEGA.bytes)
	       		  * r)) % q
		G1_SRS = UInt256(G1_SRS_X).bytes + UInt256(G1_SRS_Y).bytes
		claims_com = ec.scalar_mul(EC.BN254g1, G1_SRS, claims.bytes)

		digest = ec.add(EC.BN254g1, digest, invert(claims_com))

		points_quotient = ec.scalar_mul(EC.BN254g1, BATCH_OPENING_AT_Z, zeta.bytes)

		zeta_omega = (zeta * VK_OMEGA) % q
		r = (r * zeta_omega) % q
		add_term = ec.scalar_mul(EC.BN254g1, OPENING_AT_Z_OMEGA, r.bytes)
		points_quotient = ec.add(EC.BN254g1, points_quotient, add_term)

		digest = ec.add(EC.BN254g1, digest, points_quotient)
		quotient = invert(quotient)

		g2 = (UInt256(G2_SRS_0_X_1).bytes + UInt256(G2_SRS_0_X_0).bytes
		   + UInt256(G2_SRS_0_Y_1).bytes + UInt256(G2_SRS_0_Y_0).bytes
		   + UInt256(G2_SRS_1_X_1).bytes + UInt256(G2_SRS_1_X_0).bytes
		   + UInt256(G2_SRS_1_Y_1).bytes + UInt256(G2_SRS_1_Y_0).bytes)

		check = ec.pairing_check(EC.BN254g1, digest + quotient, g2)
		return arc4.Bool(check)



@subroutine
def expmod(base: BigUInt, exponent: BigUInt, modulus: BigUInt) -> BigUInt:
	"""Compute base^exponent % modulus."""
	result = BigUInt(1)
	while exponent > 0:
		if exponent % 2 == 1:
			result = (result * base) % modulus
		exponent = exponent // 2
		base = (base * base) % modulus
	return result

@subroutine
def curvemod(x: Bytes) -> BigUInt:
	"""Compute x % R_MOD."""
	return BigUInt.from_bytes(x) % BigUInt(R_MOD)

@subroutine
def invert(p : Bytes) -> Bytes:
	"""Invert a point on the curve."""
	x = BigUInt.from_bytes(p[:32])
	y = BigUInt.from_bytes(p[32:])
	neg_y = BigUInt(P_MOD) - y
	return x.bytes + UInt256(neg_y).bytes
