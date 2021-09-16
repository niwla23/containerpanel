import { Middleware } from '@nuxt/types'


const authMiddleware: Middleware = ({ $axios }) => {
    $axios.get("/is_authenticated").then((result)=>{
        if (!result.data.is_authenticated) {
            setTimeout(() => {
                window.location.href = "http://127.0.0.1:3000/api/oidc/authenticate"
            }, 5000);

        }
    })

}

export default authMiddleware