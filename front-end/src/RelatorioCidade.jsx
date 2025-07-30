import React, { useState } from "react";
import GraficoPorcentagem from "./GraficoPorcentagem";

function RelatorioCidade() {
  const parametros = {
    in_internet: "boolean",
    in_biblioteca: "boolean",
    in_laboratorio_informatica: "boolean",
    in_laboratorio_ciencias: "boolean",
    in_quadra_esportes: "boolean",
    in_acessibilidade_rampas: "boolean",
    qt_desktop_aluno: "int",
    qt_salas_utilizadas: "int",
  };

  const mapColunas = {
    in_internet: "Possui Internet",
    in_biblioteca: "Possui Biblioteca",
    in_laboratorio_informatica: "Possui Lab. de Informática",
    in_laboratorio_ciencias: "Possui Lab. de Ciências",
    in_quadra_esportes: "Possui Quadra de Esportes",
    in_acessibilidade_rampas: "Possui Acessibilidade (Rampas)",
    qt_desktop_aluno: "Qtd. Desktops por Aluno",
    qt_salas_utilizadas: "Qtd. Salas Utilizadas",
  };

  const [cidade, setCidade] = useState("");
  const [paran, setParan] = useState("");
  const [value, setValue] = useState("");
  const [dados, setDados] = useState([]);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPaginas, setTotalPaginas] = useState(1);
  const [porcentagem, setPorcentagem] = useState(null);

  const fetchDados = (pagina = 1) => {
    if (!cidade || !paran || value === "") {
      setError("Preencha todos os campos");
      return;
    }

    setError(null);
    let valorFinal = value;
    if (parametros[paran] === "boolean") {
      valorFinal = value === "true";
    }

    const url = new URL(
      "http://localhost:8000/relatorios/infraestrutura_das_escolas_por_municipio/"
    );
    url.searchParams.append("cidade", cidade);
    url.searchParams.append("paran", paran);
    url.searchParams.append("value", valorFinal);
    url.searchParams.append("page", pagina);

    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error("Erro ao buscar dados");
        return res.json();
      })
      .then((data) => {
        setDados(data.dados || []);
        setPage(data.pagina_atual || 1);
        setTotalPaginas(data.total_paginas || 1);
        setPorcentagem(data.porcentagem ?? null);
      })
      .catch((err) => {
        console.error(err);
        setError("Erro ao buscar dados");
      });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchDados(1); // resetar para página 1
  };

  const renderInput = () => {
    if (parametros[paran] === "boolean") {
      return (
        <select
          className="form-control"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        >
          <option value="">Selecione</option>
          <option value="true">Sim</option>
          <option value="false">Não</option>
        </select>
      );
    } else if (parametros[paran] === "int") {
      return (
        <input
          type="number"
          className="form-control"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
      );
    } else {
      return null;
    }
  };

  return (
    <div className="container mt-4">
      <h2>Relatório de Infraestrutura por Cidade</h2>

      <form onSubmit={handleSubmit} className="mb-4">
        <div className="row mb-2">
          <div className="col">
            <label>Cidade</label>
            <input
              type="text"
              className="form-control"
              value={cidade}
              onChange={(e) => setCidade(e.target.value)}
              placeholder="Digite a cidade"
            />
          </div>

          <div className="col">
            <label>Parâmetro</label>
            <select
              className="form-control"
              value={paran}
              onChange={(e) => {
                setParan(e.target.value);
                setValue("");
              }}
            >
              <option value="">Selecione</option>
              {Object.keys(parametros).map((key) => (
                <option key={key} value={key}>
                  {mapColunas[key]}
                </option>
              ))}
            </select>
          </div>

          <div className="col">
            <label>Valor</label>
            {renderInput()}
          </div>

          <div className="col d-flex align-items-end">
            <button type="submit" className="btn btn-primary w-100">
              Buscar
            </button>
          </div>
        </div>
      </form>

      {error && <p className="text-danger">{error}</p>}

      {dados.length > 0 && (
        <>
          {/* Exibe o gráfico de pizza apenas na primeira página e se houver porcentagem */}
          {page === 1 && porcentagem !== null && (
            <div className="d-flex justify-content-center mb-4">
              <GraficoPorcentagem porcentagem={porcentagem} />
            </div>
          )}
          <div className="table-responsive">
            <table className="table table-bordered table-striped">
              <thead className="thead-dark">
                <tr>
                  <th>Nome da Escola</th>
                  {Object.keys(mapColunas).map((col) => (
                    <th key={col}>{mapColunas[col]}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {dados.map((escola) => (
                  <tr key={escola.id}>
                    <td>{escola.no_entidade}</td>
                    {Object.keys(mapColunas).map((col) => (
                      <td key={col}>
                        {typeof escola[col] === "boolean"
                          ? escola[col]
                            ? "✅"
                            : "❌"
                          : escola[col]}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="d-flex justify-content-between align-items-center mt-3">
            <button
              className="btn btn-secondary"
              onClick={() => fetchDados(page - 1)}
              disabled={page <= 1}
            >
              Anterior
            </button>

            <span>
              Página {page} / {totalPaginas}
            </span>

            <button
              className="btn btn-secondary"
              onClick={() => fetchDados(page + 1)}
              disabled={page >= totalPaginas}
            >
              Próxima
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default RelatorioCidade;
