import { Middleware } from '@nuxt/types'


const authMiddleware: Middleware = ({ $axios }) => {
    $axios.get("/is_authenticated").then((result) => {
        if (!result.data.is_authenticated) {
            window.location.href = "/api/oidc/keycloak/login/?process=login"
        }
    })

}

export default authMiddleware