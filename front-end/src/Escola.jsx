// src/components/Escola.jsx
import React from 'react';

function Escola({ no_entidade, sg_uf, qt_mat_bas, no_municipio }) {
  return (
    <div className="d-flex flex-column">
      <h5 className="mb-1 fw-semibold">{no_entidade}</h5>
      <div className="d-flex justify-content-between text-secondary small">
        <span>{no_municipio}</span>
        <span className="badge bg-primary">{sg_uf}</span>
      </div>
      <div className="mt-2">
        <span className="text-muted fst-italic">{qt_mat_bas.toLocaleString()} matrículas</span>
      </div>
    </div>
  );
}

export default Escola;
