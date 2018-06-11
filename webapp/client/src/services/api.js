import axios from 'axios'

export default() => {
  return axios.create({
    baseURL: 'http://cryptohypetrader.com/api'
  })
};
