import { ApplicationModule } from './application.module';

describe('ApplicationModule', () => {
  let applicationModule: ApplicationModule;

  beforeEach(() => {
    applicationModule = new ApplicationModule();
  });

  it('should create an instance', () => {
    expect(applicationModule).toBeTruthy();
  });
});
