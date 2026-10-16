# Munteanu Ion, SI-266 - A1
s = "Salut"
b = s.encode("utf-8")
print("Text:", s)
print("Octeti:", b)
print("Primul octet:", b[0])
print("Hex:", b.hex())
print("Din hex:", bytes.fromhex(b.hex()))
