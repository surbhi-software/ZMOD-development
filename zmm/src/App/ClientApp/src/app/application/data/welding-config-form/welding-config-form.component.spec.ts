import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { WeldingConfigFormComponent } from './welding-config-form.component';

describe('WeldingConfigFormComponent', () => {
  let component: WeldingConfigFormComponent;
  let fixture: ComponentFixture<WeldingConfigFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ WeldingConfigFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(WeldingConfigFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
