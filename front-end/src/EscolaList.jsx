import React, { useState } from 'react';
import Escola from './Escola';

function EscolaList() {
  const [curso, setCurso] = useState('');
  const [escolas, setEscolas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const limit = 10;

  const buscarEscolas = (pagina = 1) => {
    if (!curso.trim()) return;

    setLoading(true);
    setError(null);

    fetch(`http://localhost:8000/escolas/curso/${encodeURIComponent(curso)}/${pagina}/${limit}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Erro na resposta da API');
        }
        return response.json();
      })
      .then(data => {
        setEscolas(data.data || []);
        setPage(pagina);
        setTotalPages(data.total_pages);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message || 'Erro ao buscar escolas');
        setLoading(false);
      });
  };

  const handlePrevious = () => {
    if (page > 1) buscarEscolas(page - 1);
  };

  const handleNext = () => {
    if (escolas.length === limit) buscarEscolas(page + 1);
  };

  return (
    <div className="container mt-5">
      <h2 className="text-center mb-4">Buscar Escolas por Curso</h2>

      <div className="row mb-4">
        <div className="col-md-8">
          <input
            type="text"
            className="form-control"
            value={curso}
            onChange={(e) => setCurso(e.target.value)}
            placeholder="Digite o nome do curso (ex: Informática)"
          />
        </div>
        <div className="col-md-4">
          <button className="btn btn-primary w-100" onClick={() => buscarEscolas(1)}>
            Buscar
          </button>
        </div>
      </div>

      {loading && <p className="text-center">Carregando...</p>}
      {error && <p className="text-danger text-center">Erro: {error}</p>}

      {!loading && !error && escolas.length === 0 && curso.trim() !== '' && (
        <p className="text-center">Nenhuma escola encontrada para o curso <strong>{curso}</strong>.</p>
      )}

      {!loading && escolas.length > 0 && (
        <>
          <div className="row g-3">
            {escolas.map((escola) => (
              <div key={escola.co_entidade} className="col-md-6">
                <div className="card shadow-sm h-100">
                  <div className="card-body">
                    <Escola
                      no_entidade={escola.no_entidade}
                      sg_uf={escola.sg_uf}
                      qt_mat_bas={escola.qt_mat_bas}
                      no_municipio={escola.no_municipio}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 d-flex justify-content-between align-items-center">
            <button
              className="btn btn-outline-secondary"
              onClick={handlePrevious}
              disabled={page === 1 || loading}
            >
             Anterior
            </button>

            <span className="fw-bold">
              Página {page} / {totalPages}
            </span>

            <button
              className="btn btn-outline-secondary"
              onClick={handleNext}
              disabled={escolas.length < limit || loading}
            >
              Próximo
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default EscolaList;
