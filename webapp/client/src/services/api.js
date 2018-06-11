import axios from 'axios'

export default() => {
  return axios.create({
    baseURL: 'cryptohypetrader.com/api'
  })
};
