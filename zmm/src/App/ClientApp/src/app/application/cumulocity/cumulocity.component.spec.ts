import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CumulocityComponent } from './cumulocity.component';

describe('CumulocityComponent', () => {
  let component: CumulocityComponent;
  let fixture: ComponentFixture<CumulocityComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CumulocityComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CumulocityComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
