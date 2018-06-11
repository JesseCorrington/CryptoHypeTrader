import axios from 'axios'

// TODO: use local IP, port 80 and have nginx forward /api to :5000/api

export default() => {
  return axios.create({
    baseURL: 'http://138.68.231.32:5000/api'
  })
}
