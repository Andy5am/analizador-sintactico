# Andy Castillo 18040

class Parser():
	def __init__(self, tokens):
		self.tokens = tokens
		self.current_token_index = 0
		self.current_token = self.tokens[self.current_token_index]
		self.EstadoInicial()

	def update_current_token(self):
		if self.current_token_index < len(self.tokens) - 1:
			self.current_token_index += 1
			self.current_token = self.tokens[self.current_token_index]

	def EstadoInicial(self):
		if self.current_token["type"] not in ['numeroToken']:
			print("Error sintactico")
		while self.current_token['type'] in ['numeroToken']:
			self.Instruccion()

			if self.current_token["value"] == ";":
				self.update_current_token()

	def Instruccion(self):
		resultado = 0
		resultado = self.Expresion(resultado)
		print("Resultado: ", resultado)

	def Expresion(self, resultado):
		resultado1, resultado2 = 0, 0
		resultado1 = self.Termino(resultado1)
		while self.current_token['value'] in ['+']:

			if self.current_token["value"] == "+":
				self.update_current_token()
				resultado2 = self.Termino(resultado2)
				resultado1 += resultado2
				print("Termino: ", resultado1)

		return resultado1
		print("Termino: ", resultado)

	def Termino(self, resultado):
		resultado1, resultado2 = 0, 0
		resultado1 = self.Factor(resultado1)
		while self.current_token['value'] in ['*']:

			if self.current_token["value"] == "*":
				self.update_current_token()
				resultado2 = self.Factor(resultado2)
				resultado1 *= resultado2
				print("Factor: ", resultado1)

		return resultado1
		print("Factor: ", resultado)

	def Factor(self, resultado):
		resultado1 = 0
		resultado1 = self.Numero(resultado1)
		return resultado1
		print("Numero: ", resultado)

	def Numero(self, resultado):
		numeroToken = None
		if self.current_token["type"] == "numeroToken":
			numeroToken = float(self.current_token["value"])
			self.update_current_token()
		return numeroToken
		print("Token: ", resultado)

Parser([{'type': '+', 'value': '+'}, {'type': 'numeroToken', 'value': '7'}, {'type': '+', 'value': '+'}, {'type': 'numeroToken', 'value': '4'}, {'type': 'por', 'value': '*'}, {'type': 'numeroToken', 'value': '5'}, {'type': 'f', 'value': ';'}, {'type': 'numeroToken', 'value': '8'}, {'type': 'por', 'value': '*'}, {'type': 'numeroToken', 'value': '3'}, {'type': 'f', 'value': ';'}, {'type': 'numeroToken', 'value': '15'}, {'type': 'f', 'value': ';'}])
