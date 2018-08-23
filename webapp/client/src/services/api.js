import axios from 'axios'

export default() => {
    var host = "http://cryptohypetrader.com";
    if (process.env.NODE_ENV === 'development') {
        host = "http://localhost:5000";
    }

    return axios.create({
        baseURL: host + "/api"
    })
};
