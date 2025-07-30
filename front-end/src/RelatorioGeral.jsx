import React, { useState, useEffect } from 'react';

function RelatorioGeral() {
  const [relatorio, setRelatorio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/relatorios/geral')
      .then((res) => {
        if (!res.ok) throw new Error('Erro na resposta da API');
        return res.json();
      })
      .then((data) => {
        setRelatorio(data);
        setLoading(false);
      })
      .catch((err) => {
        setError('Erro ao buscar dados do relatório');
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Carregando...</p>;
  if (error) return <p className="text-danger">Erro: {error}</p>;
  if (!relatorio) return null;

  const {
    resumo_geral,
    escolas_por_uf,
    matriculas_por_modalidade,
    infraestrutura_percentuais,
    escolas_por_dependencia,
    escolas_por_localizacao
  } = relatorio;

  return (
    <div className="container mt-5">
      <h2 className="mb-4 text-center">Relatório Geral da Educação no Brasil</h2>

      <section className="mb-5">
        <h4 className="mb-3">Resumo Geral</h4>
        <div className="row g-3">
          {Object.entries({
            'Total de Escolas': resumo_geral.total_escolas,
            'Total de Infraestruturas': resumo_geral.total_infraestruturas,
            'Ofertas por Modalidade': resumo_geral.total_ofertas_modalidade,
            'Cursos Técnicos': resumo_geral.total_cursos_tecnicos,
            'Relações Escola-Curso': resumo_geral.total_relacoes_escola_curso,
          }).map(([label, value]) => (
            <div className="col-md-4" key={label}>
              <div className="card shadow-sm">
                <div className="card-body">
                  <h6 className="card-title">{label}</h6>
                  <p className="card-text fw-bold fs-5">{value.toLocaleString()}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="mb-5">
        <h4 className="mb-3">Total de Escolas por UF</h4>
        <div className="row g-3">
          {escolas_por_uf.map((uf) => (
            <div className="col-md-3 col-sm-6" key={uf.uf}>
              <div className="card">
                <div className="card-body text-center">
                  <h6 className="card-title">{uf.uf}</h6>
                  <p className="card-text">{uf.total_escolas.toLocaleString()} escolas</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="mb-5">
        <h4 className="mb-3">Matrículas por Modalidade</h4>
        <ul className="list-group">
          {matriculas_por_modalidade.map((m) => (
            <li key={m.modalidade} className="list-group-item d-flex justify-content-between">
              <span>{m.modalidade_nome}</span>
              <strong>{m.total_matriculas.toLocaleString()} matrículas</strong>
            </li>
          ))}
        </ul>
      </section>

      <section className="mb-5">
        <h4 className="mb-3">Infraestrutura Escolar</h4>
        <ul className="list-group">
          <li className="list-group-item d-flex justify-content-between">
            <span>Com Internet</span>
            <strong>{infraestrutura_percentuais.com_internet}%</strong>
          </li>
          <li className="list-group-item d-flex justify-content-between">
            <span>Com Biblioteca</span>
            <strong>{infraestrutura_percentuais.com_biblioteca}%</strong>
          </li>
          <li className="list-group-item d-flex justify-content-between">
            <span>Com Laboratório de Informática</span>
            <strong>{infraestrutura_percentuais.com_laboratorio_informatica}%</strong>
          </li>
        </ul>
      </section>

      <section className="mb-5">
        <h4 className="mb-3">Escolas por Dependência Administrativa</h4>
        <ul className="list-group">
          {escolas_por_dependencia.map((d) => (
            <li key={d.tipo_dependencia} className="list-group-item d-flex justify-content-between">
              <span>{d.dependencia_nome}</span>
              <strong>{d.total_escolas.toLocaleString()} escolas</strong>
            </li>
          ))}
        </ul>
      </section>

      <section className="mb-5">
        <h4 className="mb-3">Escolas por Localização</h4>
        <ul className="list-group">
          {escolas_por_localizacao.map((l) => (
            <li key={l.tipo_localizacao} className="list-group-item d-flex justify-content-between">
              <span>{l.localizacao_nome}</span>
              <strong>{l.total_escolas.toLocaleString()} escolas</strong>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

export default RelatorioGeral;
