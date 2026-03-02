# Los_alfas(Integrantes del equipo)
Adrian_Reig,Carlos Juan Battistini,Rodrigo_Yamill

## Tema de los alfas.
Queremos hacer una aplicacion que se dedique a ver el mercado en tiempo real pudiendo asi ayudar a que producto es mas recomendable invertir si en lo seguro(etf(sp500)) o a lo ariesgado comprando acciones de empresas mundiales(nvidia). Para esos datos, esta aplicacion recopilara periodicos munidales, para que cuando se produzca una subida o bajada de las acciones, se vendan o compren(saltara una alerta en el movil).

### APIS
-Finnhub Stock API
-Yahoo Finance API (vía yfinance)

#### Desarrollo
Para poder crear esta aplicacion tenemos que coger los datos de como se encuntra el mercado a partir de la aplicacion "Finnhub Stock API"", a partir de esta aplicacion cogeremos las estadisticas o porcentajes y las comparamos las de antes vs las de ahora, a partir de esos datos se redigira a la pagina de "yahoo Finance API" para recomendar si en la bajada o subida es recomendable vender o comprar acciones tambien siguiendo la regla general y tambien si esa empresa esta en caida por temporada o por problema grave, tambien te ira recomendando la cifra que debemos invertir para compensar riesgo, si comprar una o mas acciones,o si comprar fracciones de ellas.