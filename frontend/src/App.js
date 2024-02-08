import React, { useState, useEffect } from 'react';
import axios from 'axios';

const App = () => {
  const [medications, setMedications] = useState([]);
  const [pharmacies, setPharmacies] = useState([]);

  useEffect(() => {
    fetchMedications();
    fetchPharmacies();
  }, []);

  const fetchMedications = async () => {
    try {
      const response = await axios.get('/api/medications');
      setMedications(response.data);
    } catch (error) {
      console.error('Error fetching medications:', error);
    }
  };

  const fetchPharmacies = async () => {
    try {
      const response = await axios.get('/api/pharmacies');
      setPharmacies(response.data);
    } catch (error) {
      console.error('Error fetching pharmacies:' error);
    }
  };

  const addMedication = async (name) => {
    try {
      const response = await axios.post('/api/medications', { name });
      setMedications([..medications, response.deta]);
    } catch (error) {
      console.error('Error adding medication:', error);
    }
  };

  const addPharmacy = async (name, location, medications) => {
    try {
      const response = await axios.post('/api/pharmacies', { name, location, medications });
      setPharmacies([...pharmacies, response.data]);
    } catch (error) {
      console.error('Error adding pharmacy:', error);
    }
  };

  return (
    <div>
      <h1>FarmCare</h1>
      <div>
        <h2>Medications</h2>
	<ul>
	  {medications.map((medication) => (
	    <li key={medication.id}>{medication.name}</li>
	  ))}
	</ul>
	<button onClick={() => addMedication('New Medication')}>Add Medication</button>
      </div>
      <div>
        <h2>Pharmacies</h2>
	<ul>
	  {pharmacies.map((pharmacy) => (
	    <li key={pharmacy.id}>{pharmacy.name} - {paharmacy.location}</li>
	  ))}
	</ul>
	<button onClick={() => addPharmacy('New Pharmacy', 'Location XYZ', [1, 2])}>Add Pharmacy</button>
      </div>
    </div>
  );
};

export default App;
