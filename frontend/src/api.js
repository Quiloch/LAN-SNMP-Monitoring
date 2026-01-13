import axios from 'axios';

const API_URL = "http://127.0.0.1:5000";

export const fetchDevices = async () => {
    try {
        const response = await axios.get(`${API_URL}/`);
        return response.data;
    } catch (error) {
        console.error("Error fetching devices:", error);
        return [];
    }
};

export const fetchData = async () => {
    try {
      console.log("Fetching data from:", `${API_URL}/`);
      const response = await axios.get(`${API_URL}/`);
      console.log("Response:", response.data);
      return response.data;
    } catch (error) {
      console.error("API request failed:", error);
      return null;
    }
  };
