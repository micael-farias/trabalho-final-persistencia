import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import EscolaList from './EscolaList';
import 'bootstrap/dist/css/bootstrap.min.css';
import Filtrada from './Filtrada';
import RelatorioGeral from './RelatorioGeral';
import RelatorioEstado from './RelatorioEstado';
import RelatorioCidade from './RelatorioCidade';


function App() {
  return (
    <Router>
      <div className="container mt-3">

        <nav className="mb-4">
          <Link to="/curso" className="btn btn-primary me-2">Consulta por Curso</Link>
          <Link to="/filtrada" className="btn btn-primary me-2">Consulta com filtro</Link>
          <Link to="/relatorio-geral" className="btn btn-primary me-2">Relatório Geral</Link>
          <Link to="/relatorio-cidade" className="btn btn-primary me-2">Relatório por Cidade</Link>
          <Link to="/relatorio-estado" className="btn btn-primary me-2">Relatório por Estado</Link>
          <Link to="/outra" className="btn btn-secondary">Outra Consulta</Link>

        </nav>

        <Routes>
          <Route path="/curso" element={<EscolaList />} />
          <Route path="/filtrada" element={<Filtrada />} />
          <Route path="/relatorio-geral" element={<RelatorioGeral />} />
          <Route path="/relatorio-cidade" element={<RelatorioCidade />} />
          <Route path="/relatorio-estado" element={<RelatorioEstado />} />
          <Route path="*" element={<h2>Página não encontrada</h2>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
