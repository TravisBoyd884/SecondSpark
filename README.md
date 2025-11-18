# SecondSpark
![SecondSpark Logo](front-end/public/Second.png)

**SecondSpark** is a all-in-one dashboard for ecommerce platforms including Ebay and Etsy. SecondSpark combines the listing, purchase status, sale info, and item specifications from all of the clients items selling/sold across multiple ecommerce platforms.

### Main Specifications:
SecondSpark is comprized of three main components; a Postgresql database, a back-end server written in Python using FLASK, and a web front-end using React.  

### Running The Project
*This project is dockerized*
- You can run the entire project(3 containers) with the command `docker compose up`.

**For Development:**

- You can run specific containers or servers seperatly via their respected `dockerfile`/`docker-compose.yaml` file(s) in the given directories:
    * The Python back-end is located in the `/back-end/` directory.
    * The React front-end is located in the `/front-end/` directory.
    * The Postgres database resources are located in the `/back-end/db/` directory.
