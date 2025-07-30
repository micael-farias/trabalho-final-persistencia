import React, { useState, useEffect } from 'react';
import Escola from './Escola';

function Filtrada() {
  const [filterField, setFilterField] = useState('no_municipio');
  const [query, setQuery] = useState('');
  const [escolas, setEscolas] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const limit = 10;

  const fetchData = () => {
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    fetch(`http://localhost:8000/escolas/filter/${filterField}/${query}/${page}/${limit}`)
      .then((res) => {
        if (!res.ok) throw new Error('Erro na resposta da API');
        return res.json();
      })
      .then((data) => {
        setEscolas(data.data);
        setTotalPages(data.total_pages);
        setLoading(false);
      })
      .catch((err) => {
        setError('Erro ao buscar escolas');
        console.error(err);
        setLoading(false);
      });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchData();
  };

  const handleNextPage = () => {
    if (page < totalPages) setPage((prev) => prev + 1);
  };

  const handlePreviousPage = () => {
    if (page > 1) setPage((prev) => prev - 1);
  };

  useEffect(() => {
    if (query.trim()) fetchData();
  }, [page]);

  return (
    <div className="container mt-5">
      <h2 className="text-center mb-4">Filtrar Escolas</h2>

      <form onSubmit={handleSubmit} className="mb-4">
        <div className="d-flex gap-4 justify-content-center mb-3">
          <div className="form-check">
            <input
              type="radio"
              name="filter"
              value="no_municipio"
              id="municipio"
              checked={filterField === 'no_municipio'}
              onChange={() => setFilterField('no_municipio')}
              className="form-check-input"
            />
            <label htmlFor="municipio" className="form-check-label">
              Nome do Município
            </label>
          </div>

          <div className="form-check">
            <input
              type="radio"
              name="filter"
              value="no_entidade"
              id="entidade"
              checked={filterField === 'no_entidade'}
              onChange={() => setFilterField('no_entidade')}
              className="form-check-input"
            />
            <label htmlFor="entidade" className="form-check-label">
              Nome da Escola
            </label>
          </div>
        </div>

        <div className="row justify-content-center">
          <div className="col-md-6">
            <input
              type="text"
              placeholder="Digite sua busca"
              className="form-control"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <div className="col-md-2">
            <button type="submit" className="btn btn-primary w-100">
              Buscar
            </button>
          </div>
        </div>
      </form>

      {loading && <p className="text-center">Carregando...</p>}
      {error && <p className="text-danger text-center">{error}</p>}

      {!loading && !error && escolas.length === 0 && query.trim() && (
        <p className="text-center text-muted">Nenhuma escola encontrada.</p>
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
              onClick={handlePreviousPage}
              disabled={page === 1}
            >
              Anterior
            </button>

            <span className="fw-bold">
              Página {page} / {totalPages}
            </span>

            <button
              className="btn btn-outline-secondary"
              onClick={handleNextPage}
              disabled={page === totalPages}
            >
              Próxima
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default Filtrada;
