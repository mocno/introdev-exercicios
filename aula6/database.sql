-- Entregador
CREATE TABLE IF NOT EXISTS entregador (
  entregador_id INTEGER PRIMARY KEY, -- ID do entregador
  nome TEXT, -- Nome do entregador responsável
  contato TEXT -- Contato do entregador responsável
);

-- Endereço
CREATE TABLE IF NOT EXISTS endereco (
    endereco_id INTEGER PRIMARY KEY,
    rua TEXT NOT NULL,
    numero TEXT NOT NULL,
    bairro TEXT NOT NULL,
    cidade TEXT NOT NULL,
    cep TEXT NOT NULL
);

-- Cliente
CREATE TABLE IF NOT EXISTS cliente (
  cliente_id INTEGER PRIMARY KEY, -- ID do cliente
  nome TEXT, -- Nome do cliente
  contato TEXT, -- Informações de contato do cliente
  endereco_id INTEGER NOT NULL, -- Endereço do cliente

  FOREIGN KEY (endereco_id) REFERENCES endereco(endereco_id)
);

-- Vendedor
CREATE TABLE IF NOT EXISTS vendedor (
  vendedor_id INTEGER PRIMARY KEY, -- ID do vendedor
  nome TEXT, -- Nome do vendedor
  contato TEXT -- Contato do vendedor
);

-- Fabricante
CREATE TABLE IF NOT EXISTS fabricante (
  fabricante_id INTEGER PRIMARY KEY, -- ID do fabricante
  nome TEXT -- Nome do fabricante
);

-- Produto
CREATE TABLE IF NOT EXISTS produto (
  produto_id INTEGER PRIMARY KEY, -- ID do produto
  nome TEXT, -- Nome do produto
  fabricante_id INTEGER NOT NULL, -- ID apontando para um fabricante

  FOREIGN KEY (fabricante_id) REFERENCES fabricante(fabricante_id)
);

CREATE TABLE IF NOT EXISTS pedido (
    pedido_id INTEGER PRIMARY KEY,

    status_entrega TEXT NOT NULL,

    entregador_id INTEGER NOT NULL,
    cliente_id INTEGER NOT NULL,
    vendedor_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,

    FOREIGN KEY (entregador_id) REFERENCES entregador(entregador_id),
    FOREIGN KEY (cliente_id) REFERENCES cliente(cliente_id),
    FOREIGN KEY (vendedor_id) REFERENCES vendedor(vendedor_id),
    FOREIGN KEY (produto_id) REFERENCES produto(produto_id)
);
