import './App.css';
import BookPage from './components/BookComponent';
import SearchPage from './components/SearchComponent';
import Navbar from './components/page/Navbar';
import Footer from './components/page/Footer';
import Home from './components/page/Home';
import SparqlTest from './components/SparqlTest';
import Work from './components/WorkComponent';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import CompetencyQuestionComponent from './components/CompetencyQuestionComponent';

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path='/' element={<Home />} />
        <Route index element={<Home />} />
        <Route path='ExploreAWork' element={<BookPage />} />
        <Route path='ExploreTheCorpus' element={<SearchPage />} />
        <Route path='CompetencyQuestion' element={<CompetencyQuestionComponent />} />
        <Route path='SPARQLJS' element={< SparqlTest />} />
        <Route path='Work' element={<Work />} />
      </Routes>
      <Footer />
    </BrowserRouter>

  );
}

export default App;
