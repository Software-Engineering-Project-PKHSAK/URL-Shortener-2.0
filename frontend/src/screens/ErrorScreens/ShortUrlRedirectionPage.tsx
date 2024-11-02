export const ShortUrlRedirectionPage = () => {
  return (
    <section className="page_404">
      <div className="container">
        <div className="row justify-content-center align-items-center">
          <div className="col-sm-8 text-center">
            <div className="four_zero_four_bg">
              <h1 className="text-center ">404</h1>
            </div>

            <div className="contant_box_404">
              <h3 className="h2">Look like you're lost</h3>

              <p>Sorry, the page you're looking for is disabled and expired.</p>

              <a href="/" className="link_404">
                Go to Home
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ShortUrlRedirectionPage;
